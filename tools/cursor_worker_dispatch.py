#!/usr/bin/env python3
"""Dispatch L3b worker via Cursor SDK after PM review gate (Phase 6).

Usage:
  python tools/cursor_worker_dispatch.py --parent <PM_CHILD_GID> --department development --dry-run
  python tools/cursor_worker_dispatch.py --parent <PM_CHILD_GID> --department development -y

Requires CURSOR_API_KEY for -y. Without it: SKIP exit 0.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from pm_emit_worker_prompt import DEPT_PM, emit_snippet, _run_fetch_assignee, _run_fetch_list  # noqa: E402
from cursor_sdk_kick import kick_prompt  # noqa: E402


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


def dispatch_cursor(prompt: str) -> int:
    return kick_prompt(
        prompt,
        cwd=ROOT,
        label="KICK",
        no_api_key_exit=0,
        no_sdk_exit=0,
        hint_manual="use pm_emit_worker_prompt snippet",
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Cursor SDK L3b worker dispatch")
    p.add_argument("--parent", required=True, help="PM child task GID")
    p.add_argument("--department", required=True, choices=sorted(DEPT_PM))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("-y", "--yes", action="store_true")
    args = p.parse_args()

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

    prompt = build_worker_prompt(parent=args.parent, department=args.department)
    if prompt is None:
        print(f"SKIP  no worker sub  parent={args.parent}  department={args.department}")
        return 0

    print(f"L3B  parent={args.parent}  department={args.department}")
    print(prompt)

    if args.dry_run or not args.yes:
        print("KICK  dry-run  (use -y to execute)")
        return 0
    return dispatch_cursor(prompt)


if __name__ == "__main__":
    sys.exit(main())
