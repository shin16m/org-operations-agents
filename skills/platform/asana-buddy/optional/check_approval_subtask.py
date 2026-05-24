#!/usr/bin/env python3
"""Poll an approval subtask under a parent Asana task.

Exit 0 when the matching subtask is completed (approved).
Exit 1 when found but not completed (pending).
Exit 2 when no matching subtask exists.

Usage:
  python check_approval_subtask.py --parent <GID> --marker "【レビュー】"
  python check_approval_subtask.py --parent <GID> --marker "【承認】" --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import console_safe, list_subtasks  # noqa: E402


def _find_subtask(parent_gid: str, marker: str, token: str) -> dict | None:
    matches = [
        s
        for s in list_subtasks(parent_gid, token)
        if (s.get("name") or "").strip().startswith(marker)
    ]
    if not matches:
        return None
    # Prefer incomplete first (active gate), else latest completed
    incomplete = [m for m in matches if not m.get("completed")]
    if incomplete:
        return incomplete[-1]
    return matches[-1]


def main() -> int:
    p = argparse.ArgumentParser(description="Check approval subtask completion")
    p.add_argument("--parent", required=True)
    p.add_argument("--marker", default="【承認】")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()
    sub = _find_subtask(args.parent, args.marker, token)

    if sub is None:
        result = {"status": "missing", "parent_gid": args.parent, "marker": args.marker}
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(
                console_safe(
                    f"no approval subtask under {args.parent} marker={args.marker!r}"
                ),
                file=sys.stderr,
            )
        return 2

    completed = bool(sub.get("completed"))
    result = {
        "status": "approved" if completed else "pending",
        "parent_gid": args.parent,
        "subtask_gid": str(sub.get("gid")),
        "subtask_name": (sub.get("name") or "").strip(),
        "completed": completed,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        verb = "APPROVED" if completed else "PENDING"
        print(console_safe(f"{verb} subtask={result['subtask_gid']} name={result['subtask_name']!r}"))
    return 0 if completed else 1


if __name__ == "__main__":
    sys.exit(main())
