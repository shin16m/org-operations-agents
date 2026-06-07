#!/usr/bin/env python3
"""Dispatch L3b worker via Cursor SDK after PM review gate (Phase 6).

Usage:
  python tools/cursor_worker_dispatch.py --parent <PM_CHILD_GID> --department development --dry-run
  python tools/cursor_worker_dispatch.py --parent <PM_CHILD_GID> --department development -y

Requires CURSOR_API_KEY for -y when ORG_OPS_ENFORCE_L3B=1 (default).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
for p in (str(ASANA_OPT), str(TOOLS)):
    if p not in sys.path:
        sys.path.insert(0, p)

from pm_emit_worker_prompt import DEPT_PM, emit_snippet, _run_fetch_assignee, _run_fetch_list  # noqa: E402
from cursor_sdk_kick import kick_prompt  # noqa: E402
from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402


def _first_worker_sub(parent: str, department: str) -> tuple[str, str, str] | None:
    pm_slug = DEPT_PM[department]
    for gid, name, done in _run_fetch_list(parent):
        if done:
            continue
        if name.strip().startswith(("【レビュー】", "【承認】")):
            continue
        assignee = _run_fetch_assignee(gid)
        if not assignee or assignee == pm_slug:
            continue
        return gid, name, assignee
    return None


def build_worker_prompt(*, parent: str, department: str) -> str | None:
    row = _first_worker_sub(parent, department)
    if row is None:
        return None
    gid, _name, worker = row
    return emit_snippet(
        department=department,
        parent_gid=parent,
        sub_gid=gid,
        worker_slug=worker,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Cursor SDK L3b worker dispatch")
    p.add_argument("--parent", required=True, help="PM child task GID")
    p.add_argument("--department", required=True, choices=sorted(DEPT_PM))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("-y", "--yes", action="store_true")
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()
    from execution_kick_guard import (  # noqa: WPS433
        execution_kick_allowed,
        log_blocked,
        resolve_epic_for_pm_child,
    )

    epic_gid = resolve_epic_for_pm_child(args.parent, token)
    ok, reason = execution_kick_allowed(epic_gid, token)
    if not ok:
        log_blocked(epic_gid=epic_gid, tool="cursor_worker_dispatch", reason=reason)
        return 0

    gate_cmd = [
        sys.executable,
        str(TOOLS / "check_pm_review_gate.py"),
        "--parent",
        args.parent,
    ]
    gate_rc = subprocess.run(
        gate_cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if gate_rc.returncode != 0:
        print(
            gate_rc.stdout or gate_rc.stderr or "PM review gate not approved.",
            file=sys.stderr,
        )
        return 1

    row = _first_worker_sub(args.parent, args.department)
    if row is None:
        print(f"SKIP  no worker sub  parent={args.parent}  department={args.department}")
        return 0
    worker_gid, _name, worker_slug = row
    prompt = emit_snippet(
        department=args.department,
        parent_gid=args.parent,
        sub_gid=worker_gid,
        worker_slug=worker_slug,
    )

    print(f"L3B  parent={args.parent}  department={args.department}  worker={worker_gid}")
    print(prompt)

    if args.dry_run or not args.yes:
        print("KICK  dry-run  (use -y to execute)")
        return 0

    from worker_kick_inflight import claim_worker_kick, release_worker_kick  # noqa: WPS433

    claimed, inflight_reason = claim_worker_kick(
        worker_gid,
        epic_gid=epic_gid,
        pm_child_gid=args.parent,
        tool="cursor_worker_dispatch",
    )
    if not claimed:
        print(f"SKIP  worker_inflight  worker={worker_gid}  reason={inflight_reason}")
        return 0

    enforce = os.environ.get("ORG_OPS_ENFORCE_L3B", "1").strip().lower() not in (
        "0",
        "false",
        "no",
    )
    rc = kick_prompt(
        prompt,
        cwd=ROOT,
        label="KICK",
        no_api_key_exit=2 if enforce else 0,
        no_sdk_exit=2 if enforce else 0,
        hint_manual="use pm_emit_worker_prompt snippet",
    )
    if rc != 0:
        release_worker_kick(worker_gid)
    return rc


if __name__ == "__main__":
    sys.exit(main())
