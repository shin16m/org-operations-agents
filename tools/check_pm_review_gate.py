#!/usr/bin/env python3
"""Check PM assign-review gate subtask completion.

Exit 0 when no gate sub exists (opt-out default) or when gate is complete.
Exit 1 when gate exists and is pending.

Usage:
  python tools/check_pm_review_gate.py --parent <PM子GID>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
OPTIONAL = ROOT / "skills/platform/asana-buddy/optional"
for p in (str(TOOLS), str(OPTIONAL)):
    if p not in sys.path:
        sys.path.insert(0, p)

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import console_safe  # noqa: E402
from pm_review_gate_util import find_pm_assign_review_gate_sub  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Check PM assign-review gate")
    p.add_argument("--parent", required=True)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()
    sub = find_pm_assign_review_gate_sub(args.parent, token)

    if sub is None:
        result = {"status": "skipped", "parent_gid": args.parent, "reason": "no_gate_sub"}
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(console_safe("SKIP  pm_review_gate  reason=no_gate_sub  (opt-out default OK)"))
        return 0

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
