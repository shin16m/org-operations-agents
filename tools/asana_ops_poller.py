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
TOOLS = ROOT / "tools"
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
ORG_OS_SRC = ROOT / "products/org-os/src"
if str(ORG_OS_SRC) not in sys.path:
    sys.path.insert(0, str(ORG_OS_SRC))
for p in (str(ASANA_OPT), str(ROOT), str(TOOLS)):
    if p not in sys.path:
        sys.path.append(p)

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

from wakuoke_resume_scan import print_scan_actions, scan_ready_actions  # noqa: E402
from org_os.asana_client import resolve_epic_gid  # noqa: E402
from org_os import syscall  # noqa: E402

SESSIONS_DIR = ROOT / "output/platform/sessions"
INTAKE_MARKER = "intake 元タスクとして org-ops エピック"
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
        from win_subprocess import run as win_run  # noqa: WPS433

        return win_run(
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
    from win_subprocess import run as win_run  # noqa: WPS433

    r = win_run(cmd, cwd=str(ROOT))
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
    """Return 'approved' | 'pending' | 'missing' (uses session.approval_sub_gid)."""
    import asana_ops_sessions  # noqa: WPS433

    status = asana_ops_sessions.approval_sub_resume_status(session, token)
    if status == "resumable":
        return "approved"
    if status == "wait":
        return "pending"
    return "missing"


def run_session_approval_helper(session: dict, *, dry_run: bool) -> int:
    """Invoke approval_helper --once for a suspended session (wait_target parent)."""
    parent = str(session.get("parent_gid") or "")
    sub = str(session.get("approval_sub_gid") or "")
    gate = str(session.get("gate_kind") or "planning_approval")
    if not parent or not sub:
        return 2
    cmd = [
        sys.executable,
        str(ROOT / "tools/approval_helper.py"),
        "--parent",
        parent,
        "--approval-sub",
        sub,
        "--gate-kind",
        gate,
        "--once",
    ]
    if dry_run:
        print(f"HELPER  dry-run  parent={parent}  sub={sub}  gate={gate}")
        return 0
    from win_subprocess import run as win_run  # noqa: WPS433

    r = win_run(cmd, cwd=str(ROOT), env=_subprocess_env())
    return r.returncode


def _org_os_start(epic_gid: str, *, dry_run: bool) -> int:
    cmd = [sys.executable, str(ROOT / "tools/run_org_os.py"), "dispatch", "--epic", epic_gid]
    if dry_run:
        cmd.append("--dry-run")
    r = _run_capture(cmd, label=f"org_os_start_{epic_gid}")
    if r.returncode == 0:
        tail = (r.stdout or "").strip().splitlines()
        detail = tail[-1] if tail else "ok"
        print(f"START  epic={epic_gid}  {detail}")
    else:
        print(f"WARN  START failed  epic={epic_gid}  exit={r.returncode}", file=sys.stderr)
        if r.stderr:
            print(r.stderr.strip(), file=sys.stderr)
    return r.returncode


def _auto_kick_enabled(cursor_kick_flag: bool) -> bool:
    if cursor_kick_flag:
        return True
    return os.environ.get("ORG_OPS_AUTO_KICK", "").strip().lower() in ("1", "true", "yes")


def _infer_department_for_task(task_gid: str, token: str) -> str | None:
    from dispatch_prompt_util import infer_department, load_organizations  # noqa: WPS433

    from asana_program_common import fetch_task  # noqa: WPS433

    data = fetch_task(task_gid, token)
    org = load_organizations()
    return infer_department(
        notes=str(data.get("notes") or ""),
        title=str(data.get("name") or ""),
        pillar_defaults=org.get("pillar_defaults"),
    )


def _log_kick_subprocess(
    r: subprocess.CompletedProcess[str],
    *,
    parent: str,
    gate: str,
    label: str,
) -> None:
    print(f"KICK  parent={parent}  gate={gate}  exit={r.returncode}")
    stdout = (r.stdout or "").strip()
    stderr = (r.stderr or "").strip()
    if stdout:
        for line in stdout.splitlines()[-10:]:
            print(console_safe(f"KICK  stdout  {line}"))
    if stderr:
        for line in stderr.splitlines()[-10:]:
            print(console_safe(f"KICK  stderr  {line}"), file=sys.stderr)
    if r.returncode != 0:
        print(f"WARN  kick_failed  parent={parent}  label={label}", file=sys.stderr)


def _epic_has_open_planning_approval(parent: str, token: str) -> bool:
    """True when an incomplete 【承認】 sub exists under the epic."""
    from check_approval_subtask import _find_subtask  # noqa: WPS433

    sub = _find_subtask(parent, "【承認】", token)
    return sub is not None and not sub.get("completed")


def _warn_planning_stuck_without_approval(
    parent: str,
    planning_child: str | None,
    token: str,
) -> None:
    """Epic in planning phase but no 【承認】 gate sub yet (bootstrap-only stuck)."""
    if _epic_has_open_planning_approval(parent, token):
        return
    from check_approval_subtask import _find_subtask  # noqa: WPS433

    any_approval = _find_subtask(parent, "【承認】", token)
    if any_approval and any_approval.get("completed"):
        return
    child = planning_child or "-"
    print(
        f"WARN  planning_stuck  parent={parent}  planning_child={child}  "
        f"reason=no_open_approval_sub  bootstrap_only_until_planning_pm_gate",
        file=sys.stderr,
    )
    print(
        "WARN  planning_stuck  next=planning-pm Handoff → plan-review → handoff_to_asana (or opt-in create_planning_approval_gate)",
        file=sys.stderr,
    )


def _cursor_kick_hint(item: dict, *, execute: bool, dry_run: bool, token: str | None = None) -> None:
    parent = str(item.get("parent_gid") or "")
    phase = item.get("phase") or "execution"
    gate = item.get("gate_kind") or "-"
    child = item.get("planning_child_gid") or ""

    if gate == "pm_review_gate":
        dept = item.get("department")
        if not dept and token:
            dept = _infer_department_for_task(parent, token)
        dept = dept or "development"
        cmd = [
            sys.executable,
            str(ROOT / "tools/cursor_worker_dispatch.py"),
            "--parent",
            parent,
            "--department",
            dept,
        ]
        label = f"cursor_worker_{parent}"
    elif phase == "planning":
        cmd = [
            sys.executable,
            str(ROOT / "tools/cursor_epic_dispatch.py"),
            "--epic",
            parent,
            "--mode",
            "planning",
        ]
        if child:
            cmd.extend(["--planning-child", child])
        label = f"cursor_kick_{parent}"
    elif gate == "planning_approval":
        # Post-approval RESUME: execution children do not exist yet —
        # handoff_to_asana must materialize them from the approved Handoff
        # before task_dispatcher has any target. Kick the workflow-orchestrator
        # agent (handoff_to_asana → task_dispatcher) instead of dispatching
        # directly, which would just print "DISPATCH no target".
        cmd = [
            sys.executable,
            str(ROOT / "tools/cursor_epic_dispatch.py"),
            "--epic",
            parent,
            "--mode",
            "execution",
            "--gate-kind",
            "planning_approval",
        ]
        label = f"cursor_exec_{parent}"
    else:
        cmd = [
            sys.executable,
            str(ROOT / "tools/task_dispatcher.py"),
            "--parent",
            parent,
            "--kick",
        ]
        label = f"task_dispatcher_{parent}"

    if execute and os.environ.get("CURSOR_API_KEY", "").strip() and not dry_run:
        cmd.append("-y")
        r = _run_capture(cmd, label=label)
        _log_kick_subprocess(r, parent=parent, gate=gate, label=label)
        if r.returncode != 0 and phase == "planning":
            _emit_planning_dispatch_snippet(parent, child or None)
    else:
        reason = "dry_run" if dry_run else "CURSOR_API_KEY unset"
        print(f"HINT  kick  parent={parent}  gate={gate}  reason={reason}  cmd={' '.join(cmd)} -y")
        if phase == "planning":
            _emit_planning_dispatch_snippet(parent, child or None)


def _session_auto_kick(session: dict, *, execute: bool, dry_run: bool, token: str) -> None:
    gate = session.get("gate_kind") or "planning_approval"
    parent = str(session.get("parent_gid") or "")
    item = {
        "parent_gid": parent,
        "gate_kind": gate,
        "phase": "execution" if gate != "planning_approval" else "execution",
        "department": session.get("department"),
    }
    if gate == "planning_approval":
        item["phase"] = "execution"
    _cursor_kick_hint(item, execute=execute, dry_run=dry_run, token=token)


def _emit_planning_dispatch_snippet(parent: str, planning_child: str | None) -> None:
    child = planning_child or "<planning-child-gid>"
    print(
        f"""【PlanningDispatch】parent={parent}  planning_child={child}

新規 Cursor セッションで planning-pm dispatch:

planning-pm として子タスク GID {child} を進めてください。
planning-delivery workflow に従い、Handoff 作成から Asana タスク化まで実行します。
""",
        file=sys.stderr,
    )


def _emit_epic_dispatch_snippet(item: dict) -> None:
    parent = item.get("parent_gid") or "?"
    nxt = item.get("next") or "task-dispatcher"
    gate = item.get("gate_kind") or "-"
    result = item.get("result") or "fresh"
    act = item.get("action") or "?"
    print(
        f"""【ResumeDispatch】parent={parent}  action={act}  result={result}  gate={gate}

新規 Cursor セッションで execution dispatch:

python tools/task_dispatcher.py --parent {parent}

# DISPATCH next={nxt}
""",
        file=sys.stderr,
    )


def scan_waiting_hints(project_gid: str, token: str, *, human: bool) -> None:
    try:
        from org_os import queue as org_os_queue  # noqa: WPS433
    except ImportError as exc:
        print(f"WARN  wait_list unavailable: {exc}", file=sys.stderr)
        return
    ready_rows = org_os_queue.ready_queue(project_gid, token=token)
    waiting_rows = org_os_queue.wait_list(project_gid, token=token)
    print(
        f"DASHBOARD  project={project_gid}  ready_total={len(ready_rows)}  "
        f"waiting_total={len(waiting_rows)}"
    )
    for row in waiting_rows:
        reason = row.get("suspend_reason") or "-"
        parent = row.get("epic_gid")
        print(f"HINT  parent={parent}  tool=approval_helper  reason={reason}")
        if human and reason == "Approval":
            sub_gid = "-"
            try:
                from check_approval_subtask import _find_subtask  # noqa: WPS433

                sub = _find_subtask(str(parent), "【承認】", token)
                if sub:
                    sub_gid = str(sub.get("gid") or "-")
                    if sub.get("completed"):
                        print(
                            f"  → 承認サブ完了済み。次サイクルで approval_helper が自動実行されます "
                            f"(sub={sub_gid})",
                            file=sys.stderr,
                        )
                        continue
            except Exception:  # noqa: BLE001
                pass
            print(
                f"  → Asana で【承認】サブを complete すると watch が自動で approval_helper を実行 "
                f"(sub={sub_gid})",
                file=sys.stderr,
            )


def scan_resume_and_dispatch(
    *,
    project_gids: list[str],
    token: str,
    dry_run: bool,
    human: bool,
    max_ng: int,
    cursor_kick: bool = False,
) -> int:
    auto_kick = _auto_kick_enabled(cursor_kick)
    for project_gid in project_gids:
        scan_waiting_hints(project_gid, token, human=human)
        try:
            actions = scan_ready_actions(
                project_gid,
                token=token,
                max_ng=max_ng,
                dry_run=dry_run,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"WARN  resume_scan failed  project={project_gid}: {exc}", file=sys.stderr)
            continue
        print_scan_actions(project_gid, actions, max_ng=max_ng, dry_run=dry_run)
        for item in actions:
            act = item.get("action")
            if act not in ("READY", "RESUME"):
                continue
            parent = str(item.get("parent_gid") or "")
            phase = item.get("phase") or "execution"
            if act == "READY" and phase == "planning":
                child = item.get("planning_child_gid")
                print(
                    f"PLANNING_DISPATCH  parent={parent}  planning_child={child or '-'}  "
                    f"next=planning-pm"
                )
                if token:
                    _warn_planning_stuck_without_approval(parent, child, token)
                if human:
                    _emit_planning_dispatch_snippet(parent, child)
                if auto_kick or human:
                    _cursor_kick_hint(item, execute=auto_kick, dry_run=dry_run, token=token)
                continue
            nxt = item.get("next") or "task-dispatcher"
            result = item.get("result")
            gate = item.get("gate_kind") or "-"
            if act == "RESUME":
                _org_os_start(parent, dry_run=dry_run)
            print(
                f"DISPATCH  parent={parent}  action={act}  result={result or 'fresh'}  "
                f"gate={gate}  phase={phase}  next={nxt}"
            )
            if human:
                _emit_epic_dispatch_snippet(item)
            if auto_kick or human:
                _cursor_kick_hint(item, execute=auto_kick, dry_run=dry_run, token=token)
    return 0


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
            helper_rc = run_session_approval_helper(session, dry_run=dry_run)
            if helper_rc == 0:
                print(f"HELPER  session={sid}  parent={parent}  sub={sub}  ok")
            elif helper_rc == 1:
                print(f"HELPER  session={sid}  pending  (skipped kick)")
            else:
                print(f"WARN  HELPER  session={sid}  exit={helper_rc}", file=sys.stderr)
            # Kick/START is owned by scan_resume_and_dispatch (runner) — no _session_auto_kick here.
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
    epic_gid: str | None = None,
) -> Path:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    sid = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    data = {
        "session_id": sid,
        "state": "suspended",
        "gate_kind": gate_kind,
        "marker": marker,
        "parent_gid": parent_gid,
        "epic_gid": epic_gid or parent_gid,
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
    p.add_argument(
        "--no-scan-resume",
        action="store_true",
        help="Skip org-os resume scan + START/DISPATCH (default: scan enabled)",
    )
    p.add_argument(
        "--max-ng",
        type=int,
        default=3,
        help="NG loop limit for resume scan (default 3)",
    )
    p.add_argument(
        "--cursor-kick",
        action="store_true",
        help="When CURSOR_API_KEY set, invoke cursor_epic_dispatch after PLANNING/DISPATCH hints",
    )
    args = p.parse_args()

    if args.record_wait:
        parent, sub, url = args.record_wait
        marker = args.marker or ("【レビュー】" if args.gate_kind == "pm_review_gate" else "【承認】")
        load_env_from_dotfile()
        tok = get_token()
        epic_gid = resolve_epic_gid(parent, tok)
        if args.gate_kind == "pm_review_gate" and epic_gid != parent:
            try:
                result = syscall.suspend(epic_gid, "Human Review", ref=sub)
                print(
                    f"SUSPEND  epic={epic_gid}  os_state={result['os_state']}  "
                    f"reason={result['suspend_reason']}  wait_target={parent}"
                )
            except Exception as exc:  # noqa: BLE001
                print(
                    f"WARN  epic suspend failed epic={epic_gid}: {exc}",
                    file=sys.stderr,
                )
        path = save_suspend_session(
            parent_gid=parent,
            approval_sub_gid=sub,
            approval_url=url,
            gate_kind=args.gate_kind,
            marker=marker,
            department=args.department,
            epic_gid=epic_gid,
        )
        print(f"WAIT  session saved  path={path}  gate={args.gate_kind}  epic={epic_gid}")
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
        code = scan_projects(
            project_gids=project_gids,
            token=token,
            dry_run=args.dry_run,
            human=args.human,
            trigger_gid=args.trigger_intake,
            auto_bootstrap=args.auto_bootstrap,
            yes=args.yes,
        )
        if code != 0:
            return code
        if not args.no_scan_resume and not args.trigger_intake and not args.auto_bootstrap:
            return scan_resume_and_dispatch(
                project_gids=project_gids,
                token=token,
                dry_run=args.dry_run,
                human=args.human,
                max_ng=args.max_ng,
                cursor_kick=args.cursor_kick,
            )
        return 0

    if args.once:
        return _run()

    while True:
        code = _run()
        if code != 0:
            return code
        time.sleep(max(5, args.interval))


if __name__ == "__main__":
    sys.exit(main())
