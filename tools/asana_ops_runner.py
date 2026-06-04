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
for p in (str(ROOT), str(TOOLS), str(ASANA_OPT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import resolve_project_with_fallback  # noqa: E402

import asana_ops_sessions  # noqa: E402
from asana_ops_poller import (  # noqa: E402
    _auto_kick_enabled,
    scan_projects,
    scan_resume_and_dispatch,
)


def run_approval_helper_pass(*, dry_run: bool) -> int:
    """Run approval_helper --once for sessions whose gate subtask is complete."""
    load_env_from_dotfile()
    token = get_token()
    ran = 0
    for session in asana_ops_sessions.load_suspended_sessions():
        status = asana_ops_sessions.check_session_status(session, token)
        if status.get("status") != "resumable":
            continue
        parent = str(session.get("epic_gid") or session.get("parent_gid") or "")
        sub = str(session.get("approval_sub_gid") or "")
        gate = str(session.get("gate_kind") or "planning_approval")
        if not parent or not sub:
            continue
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
            print(f"HELPER  dry-run  parent={parent}  sub={sub}  gate={gate}")
            ran += 1
            continue
        print(f"HELPER  run  parent={parent}  sub={sub}")
        r = subprocess.run(cmd, cwd=str(ROOT), env=_subprocess_env())
        if r.returncode == 0:
            ran += 1
    return ran


def _subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


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

    helper_ran = run_approval_helper_pass(dry_run=dry_run)
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
