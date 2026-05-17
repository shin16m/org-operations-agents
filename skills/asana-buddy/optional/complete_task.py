#!/usr/bin/env python3
"""Mark an Asana task completed (for task-executor)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import console_safe, set_task_completed  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Set Asana task completed flag")
    p.add_argument("--gid", required=True, help="Task GID")
    p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    p.add_argument("--undo", action="store_true", help="Mark incomplete")
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()
    completed = not args.undo

    if not args.yes:
        verb = "完了" if completed else "未完了"
        print(console_safe(f"タスク {args.gid} を{verb}にしますか? (y/N): "), end="")
        if input().strip().lower() != "y":
            print("abort")
            sys.exit(0)

    data = set_task_completed(args.gid, completed, token)
    print("updated", data.get("gid"), "completed=", data.get("completed"))


if __name__ == "__main__":
    main()
