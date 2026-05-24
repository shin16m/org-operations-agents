#!/usr/bin/env python3
"""Scan Asana project for intake candidates (Agent Type=AI · Task Type=Intake); monitor sessions.

Usage:
  python tools/asana_ops_poller.py --once
  python tools/asana_ops_poller.py --once --dry-run --human
  python tools/asana_ops_poller.py --watch --interval 60
  python tools/asana_ops_poller.py --once --trigger-intake 1215082835252575
  python tools/asana_ops_poller.py --once --auto-bootstrap --dry-run
  python tools/asana_ops_poller.py --once --auto-bootstrap -y
  python tools/asana_ops_poller.py --once --projects 1214771428861230,OTHER_ID

Output lines (UX SSOT): SCAN · SKIP · INTAKE · DISPATCH · WAIT · RESUME
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
if str(ASANA_OPT) not in sys.path:
    sys.path.insert(0, str(ASANA_OPT))

import requests  # noqa: E402

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    ASANA_BASE,
    assignee_type_config,
    console_safe,
    list_task_comment_stories,
    resolve_project_with_fallback,
    task_type_config,
)

SESSIONS_DIR = ROOT / "output/platform/sessions"
INTAKE_MARKER = "intake 元タスクとして org-ops エピック"
EPIC_PREFIX = "【org-ops】"
OPT_FIELDS = "name,gid,completed,parent,permalink_url,custom_fields,custom_fields.enum_value,custom_fields.enum_value.gid"


def _assignee_kind(task: dict, cfg: dict[str, str] | None) -> str | None:
    if not cfg:
        return None
    for cf in task.get("custom_fields") or []:
        if str(cf.get("gid")) != cfg["field_gid"]:
            continue
        ev = cf.get("enum_value") or {}
        if str(ev.get("gid")) == cfg["ai_gid"]:
            return "AI"
        if str(ev.get("gid")) == cfg["human_gid"]:
            return "human"
        name = (ev.get("name") or cf.get("display_value") or "").strip()
        if name.upper() == "AI":
            return "AI"
        if name.lower() == "human":
            return "human"
        return name or None
    return None


def _task_type_kind(task: dict, cfg: dict[str, str] | None) -> str | None:
    if not cfg:
        return None
    for cf in task.get("custom_fields") or []:
        if str(cf.get("gid")) != cfg["field_gid"]:
            continue
        ev = cf.get("enum_value") or {}
        if str(ev.get("gid")) == cfg["intake_gid"]:
            return "Intake"
        if str(ev.get("gid")) == cfg["epic_gid"]:
            return "Epic"
        name = (ev.get("name") or cf.get("display_value") or "").strip()
        if name.lower() == "intake":
            return "Intake"
        if name.lower() == "epic":
            return "Epic"
        return name or None
    return None


def list_project_tasks(project_gid: str, token: str) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    rows: list[dict] = []
    offset = None
    while True:
        params: dict = {"opt_fields": OPT_FIELDS, "limit": 100}
        if offset:
            params["offset"] = offset
        r = requests.get(
            f"{ASANA_BASE}/projects/{project_gid}/tasks",
            headers=headers,
            params=params,
        )
        r.raise_for_status()
        body = r.json()
        rows.extend(body.get("data") or [])
        offset = (body.get("next_page") or {}).get("offset")
        if not offset:
            break
    return rows


def already_intake_source(task_gid: str, token: str) -> bool:
    for story in list_task_comment_stories(task_gid, token):
        text = story.get("text") or ""
        if INTAKE_MARKER in text:
            return True
    return False


def _subprocess_env() -> dict[str, str]:
    return {**os.environ, "PYTHONIOENCODING": "utf-8"}


def _run_capture(cmd: list[str], *, label: str) -> subprocess.CompletedProcess[str]:
    """Run a repo Python helper; never raise on Windows decode quirks."""
    try:
        return subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_subprocess_env(),
        )
    except Exception as exc:  # noqa: BLE001 — poller must keep scanning
        print(f"WARN  {label}  subprocess_err={exc}", file=sys.stderr)
        return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr=str(exc))


def is_candidate(
    task: dict,
    at_cfg: dict[str, str] | None,
    tt_cfg: dict[str, str] | None,
) -> tuple[bool, str]:
    if task.get("completed"):
        return False, "completed"
    if task.get("parent"):
        return False, "subtask"
    name = (task.get("name") or "").strip()
    if name.startswith(EPIC_PREFIX):
        return False, "epic"
    agent = _assignee_kind(task, at_cfg)
    if agent != "AI":
        return False, "no_cf" if agent is None else f"agent_type={agent}"
    task_type = _task_type_kind(task, tt_cfg)
    if task_type != "Intake":
        return False, "no_task_type" if task_type is None else f"task_type={task_type}"
    return True, "ok"


def _emit_resume_snippet(session: dict) -> None:
    """Print Phase 2 resume snippet to stderr (--human friendly)."""
    cmd = [
        sys.executable,
        str(ROOT / "tools/pm_emit_resume_prompt.py"),
        "--session",
        session.get("session_id") or "",
    ]
    r = _run_capture(cmd, label="resume_snippet")
    stdout = r.stdout or ""
    if r.returncode == 0 and stdout.strip():
        print(stdout.strip(), file=sys.stderr)
    elif r.returncode != 0:
        print(f"WARN  resume_snippet  exit={r.returncode}", file=sys.stderr)
        if r.stderr:
            print(r.stderr.strip(), file=sys.stderr)


def trigger_intake(gid: str, *, dry_run: bool, human: bool = False) -> int:
    out = ROOT / "output/platform/intake" / f"{gid}-snapshot.json"
    cmd = [
        sys.executable,
        str(ROOT / "tools/intake_from_asana.py"),
        "--task",
        gid,
        "--out",
        str(out),
    ]
    if dry_run:
        print(f"INTAKE  source={gid}  dry-run  would_run={' '.join(cmd)}")
        return 0
    r = _run_capture(cmd, label=f"intake_{gid}")
    if r.returncode != 0:
        print(f"INTAKE  source={gid}  ERR  exit={r.returncode}", file=sys.stderr)
        if r.stderr:
            print(r.stderr.strip(), file=sys.stderr)
        return r.returncode
    print(f"INTAKE  source={gid}  OK  snapshot={out.as_posix()}")
    if human:
        print(
            f"  → 次: 和久桶 intake-asana  Asana タスク: {gid}",
            file=sys.stderr,
        )
    return 0


def run_auto_bootstrap(gid: str, *, dry_run: bool, yes: bool) -> int:
    cmd = [sys.executable, str(ROOT / "tools/auto_intake_runner.py"), "--task", gid]
    if yes and not dry_run:
        cmd.append("-y")
    else:
        cmd.append("--dry-run")
    r = subprocess.run(cmd, cwd=str(ROOT))
    return r.returncode


def load_sessions() -> list[dict]:
    if not SESSIONS_DIR.is_dir():
        return []
    out: list[dict] = []
    for path in sorted(SESSIONS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_path"] = str(path)
            out.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return out


def check_session_resume(session: dict, token: str) -> str:
    """Return 'approved' | 'pending' | 'missing'."""
    from check_approval_subtask import _find_subtask  # noqa: WPS433

    parent = session.get("parent_gid") or ""
    marker = session.get("marker") or "【承認】"
    sub = _find_subtask(parent, marker, token)
    if sub is None:
        return "missing"
    return "approved" if sub.get("completed") else "pending"


def scan_projects(
    *,
    project_gids: list[str],
    token: str,
    dry_run: bool,
    human: bool,
    trigger_gid: str | None,
    auto_bootstrap: bool = False,
    yes: bool = False,
) -> int:
    if trigger_gid:
        if auto_bootstrap:
            return run_auto_bootstrap(trigger_gid, dry_run=dry_run, yes=yes)
        return trigger_intake(trigger_gid, dry_run=dry_run, human=human)

    cfg = assignee_type_config()
    tt_cfg = task_type_config()
    total_candidates = 0
    total_skipped = 0
    for project_gid in project_gids:
        tasks = list_project_tasks(project_gid, token)
        candidates = 0
        skipped = 0
        for task in tasks:
            ok, reason = is_candidate(task, cfg, tt_cfg)
            if ok:
                candidates += 1
            else:
                skipped += 1
                if reason not in ("completed", "subtask"):
                    gid = task.get("gid")
                    print(
                        console_safe(
                            f"SKIP  project={project_gid}  task={gid}  reason={reason}  "
                            f"name={(task.get('name') or '')[:40]!r}"
                        )
                    )
        print(f"SCAN  project={project_gid}  candidates={candidates}  skipped={skipped}")
        total_candidates += candidates
        total_skipped += skipped

        for task in tasks:
            ok, reason = is_candidate(task, cfg, tt_cfg)
            if not ok:
                continue
            gid = str(task.get("gid"))
            if already_intake_source(gid, token):
                print(f"SKIP  duplicate intake  task={gid}")
                continue
            url = task.get("permalink_url") or f"https://app.asana.com/0/0/0/{gid}"
            print(console_safe(f"CANDIDATE  project={project_gid}  task={gid}  url={url}"))
            if human:
                print(console_safe(f"  → intake 候補: {(task.get('name') or '')[:60]}"), file=sys.stderr)
            if auto_bootstrap:
                return run_auto_bootstrap(gid, dry_run=dry_run, yes=yes)

    if len(project_gids) > 1:
        print(f"SCAN  total  projects={len(project_gids)}  candidates={total_candidates}  skipped={total_skipped}")

    for session in load_sessions():
        if session.get("state") != "suspended":
            continue
        sid = session.get("session_id") or Path(session.get("_path", "")).stem
        parent = session.get("parent_gid") or "?"
        sub = session.get("approval_sub_gid") or "?"
        url = session.get("approval_url") or ""
        status = check_session_resume(session, token)
        if status == "approved":
            print(f"RESUME  session={sid}  gate={session.get('gate_kind')}  approved")
            if human:
                _emit_resume_snippet(session)
        else:
            print(f"WAIT  session={sid}  gate={session.get('gate_kind')}  sub={sub}")
            if url:
                print(f"      url={url}")
            print("      action=Complete subtask in Asana UI, then re-run poller")
            if human:
                print(
                    f"⏸ 承認待ち: {session.get('gate_kind')} — Asana で complete してください\n   {url}",
                    file=sys.stderr,
                )
    return 0


def save_suspend_session(
    *,
    parent_gid: str,
    approval_sub_gid: str,
    approval_url: str,
    gate_kind: str,
    marker: str,
    department: str | None = None,
) -> Path:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    sid = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    data = {
        "session_id": sid,
        "state": "suspended",
        "gate_kind": gate_kind,
        "marker": marker,
        "parent_gid": parent_gid,
        "approval_sub_gid": approval_sub_gid,
        "approval_url": approval_url,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if department:
        data["department"] = department
    path = SESSIONS_DIR / f"{sid}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    p = argparse.ArgumentParser(description="Asana ops poller — scan · intake trigger · suspend monitor")
    p.add_argument("--once", action="store_true", help="Single scan pass")
    p.add_argument("--watch", action="store_true", help="Repeat scan")
    p.add_argument("--interval", type=int, default=60, help="Watch interval seconds")
    p.add_argument("--project", default=None)
    p.add_argument(
        "--projects",
        metavar="GID,GID",
        help="Comma-separated project GIDs (Phase 2 multi-project scan)",
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--human", action="store_true", help="Human-readable stderr hints")
    p.add_argument("--trigger-intake", metavar="GID", help="Run intake_from_asana for one task")
    p.add_argument(
        "--auto-bootstrap",
        action="store_true",
        help="Phase 4: first CANDIDATE (or --trigger-intake GID) → auto_intake_runner",
    )
    p.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="With --auto-bootstrap: execute (default dry-run)",
    )
    p.add_argument(
        "--record-wait",
        nargs=3,
        metavar=("PARENT_GID", "SUB_GID", "URL"),
        help="Save suspended session JSON (orchestrator helper)",
    )
    p.add_argument(
        "--gate-kind",
        default="planning_approval",
        choices=("planning_approval", "pm_review_gate"),
        help="With --record-wait: session gate_kind (Phase 2)",
    )
    p.add_argument(
        "--marker",
        default=None,
        help="With --record-wait: subtask title marker (default from gate-kind)",
    )
    p.add_argument(
        "--department",
        default=None,
        help="With --record-wait --gate-kind pm_review_gate: dispatch department hint",
    )
    args = p.parse_args()

    if args.record_wait:
        parent, sub, url = args.record_wait
        marker = args.marker or ("【レビュー】" if args.gate_kind == "pm_review_gate" else "【承認】")
        path = save_suspend_session(
            parent_gid=parent,
            approval_sub_gid=sub,
            approval_url=url,
            gate_kind=args.gate_kind,
            marker=marker,
            department=args.department,
        )
        print(f"WAIT  session saved  path={path}  gate={args.gate_kind}")
        return 0

    if not args.once and not args.watch:
        p.error("use --once or --watch")

    load_env_from_dotfile()
    token = get_token()
    if args.projects:
        project_gids = [p.strip() for p in args.projects.split(",") if p.strip()]
    else:
        project_gids = [resolve_project_with_fallback(args.project)]

    def _run() -> int:
        return scan_projects(
            project_gids=project_gids,
            token=token,
            dry_run=args.dry_run,
            human=args.human,
            trigger_gid=args.trigger_intake,
            auto_bootstrap=args.auto_bootstrap,
            yes=args.yes,
        )

    if args.once:
        return _run()

    while True:
        code = _run()
        if code != 0:
            return code
        time.sleep(max(5, args.interval))


if __name__ == "__main__":
    sys.exit(main())
