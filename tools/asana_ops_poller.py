#!/usr/bin/env python3
"""Scan Asana project for AI intake candidates; monitor suspended workflow sessions.

Usage:
  python tools/asana_ops_poller.py --once
  python tools/asana_ops_poller.py --once --dry-run --human
  python tools/asana_ops_poller.py --watch --interval 60
  python tools/asana_ops_poller.py --once --trigger-intake 1215082835252575

Output lines (UX SSOT): SCAN · SKIP · INTAKE · WAIT · RESUME
"""
from __future__ import annotations

import argparse
import json
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
    list_task_comment_stories,
    resolve_project_with_fallback,
)

SESSIONS_DIR = ROOT / "output/platform/sessions"
INTAKE_MARKER = "intake 元タスクとして org-ops エピック"
EPIC_PREFIX = "【org-ops】"
OPT_FIELDS = "name,gid,completed,parent,permalink_url,custom_fields,custom_fields.enum_value"


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


def is_candidate(task: dict, cfg: dict[str, str] | None) -> tuple[bool, str]:
    if task.get("completed"):
        return False, "completed"
    if task.get("parent"):
        return False, "subtask"
    name = (task.get("name") or "").strip()
    if name.startswith(EPIC_PREFIX):
        return False, "epic"
    kind = _assignee_kind(task, cfg)
    if kind != "AI":
        return False, "no_cf" if kind is None else f"cf={kind}"
    return True, "ok"


def trigger_intake(gid: str, *, dry_run: bool) -> int:
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
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print(f"INTAKE  source={gid}  ERR  exit={r.returncode}", file=sys.stderr)
        if r.stderr:
            print(r.stderr.strip(), file=sys.stderr)
        return r.returncode
    print(f"INTAKE  source={gid}  OK  snapshot={out.as_posix()}")
    return 0


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


def scan_once(
    *,
    project_gid: str,
    token: str,
    dry_run: bool,
    human: bool,
    trigger_gid: str | None,
) -> int:
    cfg = assignee_type_config()
    tasks = list_project_tasks(project_gid, token)
    candidates = 0
    skipped = 0
    for task in tasks:
        ok, reason = is_candidate(task, cfg)
        if ok:
            candidates += 1
        else:
            skipped += 1
            if reason not in ("completed", "subtask"):
                gid = task.get("gid")
                print(f"SKIP  task={gid}  reason={reason}  name={(task.get('name') or '')[:40]!r}")
    print(f"SCAN  project={project_gid}  candidates={candidates}  skipped={skipped}")

    if trigger_gid:
        return trigger_intake(trigger_gid, dry_run=dry_run)

    for task in tasks:
        ok, reason = is_candidate(task, cfg)
        if not ok:
            continue
        gid = str(task.get("gid"))
        if already_intake_source(gid, token):
            print(f"SKIP  duplicate intake  task={gid}")
            continue
        url = task.get("permalink_url") or f"https://app.asana.com/0/0/0/{gid}"
        print(f"CANDIDATE  task={gid}  url={url}")
        if human:
            print(f"  → intake 候補: {(task.get('name') or '')[:60]}", file=sys.stderr)

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
    path = SESSIONS_DIR / f"{sid}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    p = argparse.ArgumentParser(description="Asana ops poller — scan · intake trigger · suspend monitor")
    p.add_argument("--once", action="store_true", help="Single scan pass")
    p.add_argument("--watch", action="store_true", help="Repeat scan")
    p.add_argument("--interval", type=int, default=60, help="Watch interval seconds")
    p.add_argument("--project", default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--human", action="store_true", help="Human-readable stderr hints")
    p.add_argument("--trigger-intake", metavar="GID", help="Run intake_from_asana for one task")
    p.add_argument(
        "--record-wait",
        nargs=3,
        metavar=("PARENT_GID", "SUB_GID", "URL"),
        help="Save suspended session JSON (orchestrator helper)",
    )
    args = p.parse_args()

    if args.record_wait:
        parent, sub, url = args.record_wait
        path = save_suspend_session(
            parent_gid=parent,
            approval_sub_gid=sub,
            approval_url=url,
            gate_kind="planning_approval",
            marker="【承認】",
        )
        print(f"WAIT  session saved  path={path}")
        return 0

    if not args.once and not args.watch:
        p.error("use --once or --watch")

    load_env_from_dotfile()
    token = get_token()
    project = resolve_project_with_fallback(args.project)

    def _run() -> int:
        return scan_once(
            project_gid=project,
            token=token,
            dry_run=args.dry_run,
            human=args.human,
            trigger_gid=args.trigger_intake,
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
