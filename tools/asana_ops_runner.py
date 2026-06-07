#!/usr/bin/env python3
"""Org-ops orchestration runner — watch loop for intake · gate · kick (Phase 5).

Combines poller auto-bootstrap, approval_helper pass, resume scan, session archive.

Usage:
  python tools/asana_ops_runner.py --once --dry-run
  python tools/asana_ops_runner.py --watch --interval 60
  ORG_OPS_AUTO_KICK=1 CURSOR_API_KEY=... python tools/asana_ops_runner.py --watch

Environment:
  ORG_OPS_AUTO_KICK=1  — auto cursor_epic_dispatch when CURSOR_API_KEY is set
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
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

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import resolve_project_with_fallback  # noqa: E402

import asana_ops_sessions  # noqa: E402
from asana_ops_poller import (  # noqa: E402
    _auto_kick_enabled,
    scan_projects,
    scan_resume_and_dispatch,
)


def _invoke_approval_helper(
    *,
    parent: str,
    sub: str,
    gate: str,
    dry_run: bool,
    source: str,
) -> bool:
    cmd = [
        sys.executable,
        str(TOOLS / "approval_helper.py"),
        "--parent",
        parent,
        "--approval-sub",
        sub,
        "--gate-kind",
        gate,
        "--once",
    ]
    if dry_run:
        print(f"HELPER  dry-run  source={source}  parent={parent}  sub={sub}  gate={gate}")
        return True
    print(f"HELPER  run  source={source}  parent={parent}  sub={sub}")
    r = subprocess.run(cmd, cwd=str(ROOT), env=_subprocess_env())
    return r.returncode == 0


def run_approval_helper_pass(
    *,
    project_gids: list[str],
    token: str,
    dry_run: bool,
) -> int:
    """Run approval_helper --once when a gate subtask is complete.

    Path A: suspended session JSON (--record-wait).
    Path B: org-os wait queue (Approval) + completed 【承認】 sub — fallback when
    record-wait was skipped but Asana gate exists.
    """
    ran = 0
    seen: set[tuple[str, str]] = set()

    for session in asana_ops_sessions.load_suspended_sessions():
        status = asana_ops_sessions.check_session_status(session, token)
        if status.get("status") != "resumable":
            continue
        parent = str(session.get("parent_gid") or session.get("epic_gid") or "")
        sub = str(session.get("approval_sub_gid") or "")
        gate = str(session.get("gate_kind") or "planning_approval")
        if not parent or not sub:
            continue
        key = (parent, sub)
        if key in seen:
            continue
        seen.add(key)
        if _invoke_approval_helper(
            parent=parent, sub=sub, gate=gate, dry_run=dry_run, source="session"
        ):
            ran += 1

    try:
        from check_approval_subtask import _find_subtask  # noqa: WPS433
        from org_os import queue as org_os_queue  # noqa: WPS433
    except ImportError as exc:
        print(f"WARN  wait_queue helper skipped: {exc}", file=sys.stderr)
        return ran

    for project_gid in project_gids:
        try:
            rows = org_os_queue.wait_list(project_gid, token=token)
        except Exception as exc:  # noqa: BLE001
            print(
                f"WARN  wait_queue scan failed  project={project_gid}: {exc}",
                file=sys.stderr,
            )
            continue
        for row in rows:
            if row.get("suspend_reason") != "Approval":
                continue
            parent = str(row.get("epic_gid") or "")
            if not parent:
                continue
            sub_task = _find_subtask(parent, "【承認】", token)
            if not sub_task or not sub_task.get("completed"):
                continue
            sub = str(sub_task.get("gid") or "")
            if not sub:
                continue
            key = (parent, sub)
            if key in seen:
                continue
            seen.add(key)
            if _invoke_approval_helper(
                parent=parent,
                sub=sub,
                gate="planning_approval",
                dry_run=dry_run,
                source="wait_queue",
            ):
                ran += 1

    return ran


def _subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


# Cycle order SSOT (approval-flow.md §5.2 · B1-2):
#   1. approval_helper_pass
#   2. scan_projects (auto-bootstrap · session RESUME+HELPER)
#   3. scan_resume_and_dispatch (PLANNING_DISPATCH / DISPATCH)
#   4. scan_execution_and_kick (L3b · BLOCKED aggregated as RUNNER BLOCKED)
#   5. archive_resumable_sessions
CYCLE_ORDER = (
    "approval_helper_pass",
    "scan_projects",
    "scan_resume_and_dispatch",
    "scan_execution_and_kick",
    "archive_resumable_sessions",
)


def run_cycle(
    *,
    project_gids: list[str],
    dry_run: bool,
    yes: bool,
    human: bool,
    max_ng: int,
    cursor_kick: bool,
) -> int:
    load_env_from_dotfile()
    token = get_token()
    auto_kick = _auto_kick_enabled(cursor_kick)
    print(f"RUNNER  cycle  dry_run={dry_run}  auto_kick={auto_kick}  projects={len(project_gids)}")
    print(f"RUNNER  cycle_order  {' -> '.join(CYCLE_ORDER)}")

    helper_ran = run_approval_helper_pass(
        project_gids=project_gids,
        token=token,
        dry_run=dry_run,
    )
    print(f"RUNNER  approval_helper_pass  count={helper_ran}")

    code = scan_projects(
        project_gids=project_gids,
        token=token,
        dry_run=dry_run,
        human=human,
        trigger_gid=None,
        auto_bootstrap=True,
        yes=yes and not dry_run,
    )
    if code != 0:
        return code

    code = scan_resume_and_dispatch(
        project_gids=project_gids,
        token=token,
        dry_run=dry_run,
        human=human,
        max_ng=max_ng,
        cursor_kick=cursor_kick,
    )
    if code != 0:
        return code

    from execution_resume_scan import scan_execution_and_kick  # noqa: WPS433

    blocked_n = scan_execution_and_kick(
        project_gids=project_gids,
        token=token,
        dry_run=dry_run,
        cursor_kick=cursor_kick,
    )
    if blocked_n:
        print(f"RUNNER  execution_blocked  count={blocked_n}")

    archived = asana_ops_sessions.archive_resumable_sessions(token, dry_run=dry_run)
    print(f"RUNNER  archive  count={archived}")
    print("RUNNER  cycle  done")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Org-ops orchestration runner (Phase 5)")
    p.add_argument("--once", action="store_true")
    p.add_argument("--watch", action="store_true")
    p.add_argument("--interval", type=int, default=60)
    p.add_argument("--project", default=None)
    p.add_argument("--projects", metavar="GID,GID")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--human", action="store_true")
    p.add_argument("-y", "--yes", action="store_true", help="Execute auto-bootstrap (not dry-run)")
    p.add_argument("--cursor-kick", action="store_true", help="Force SDK kick (also: ORG_OPS_AUTO_KICK=1)")
    p.add_argument("--max-ng", type=int, default=3)
    args = p.parse_args()

    if not args.once and not args.watch:
        p.error("use --once or --watch")

    load_env_from_dotfile()
    if args.projects:
        project_gids = [x.strip() for x in args.projects.split(",") if x.strip()]
    else:
        project_gids = [resolve_project_with_fallback(args.project)]

    def _run() -> int:
        return run_cycle(
            project_gids=project_gids,
            dry_run=args.dry_run,
            yes=args.yes,
            human=args.human,
            max_ng=args.max_ng,
            cursor_kick=args.cursor_kick,
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
