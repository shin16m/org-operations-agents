#!/usr/bin/env python3
"""Update Asana task notes with 課 / 担当 / 状態 header."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    console_safe,
    fetch_task,
    merge_notes_with_assignment,
    update_task_notes,
)


def main() -> None:
    p = argparse.ArgumentParser(description="Set 課/担当/状態 on task notes")
    p.add_argument("--gid", required=True)
    p.add_argument("--department", default="analysis")
    p.add_argument("--assignee", required=True, help="agent slug, e.g. data-engineer")
    p.add_argument("--status", default="assigned")
    p.add_argument(
        "--preserve-body",
        action="store_true",
        help="Keep existing notes body below header",
    )
    p.add_argument("--notes", help="Replace entire notes (ignores preserve-body)")
    p.add_argument("-y", action="store_true", help="Apply without prompt")
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()
    task = fetch_task(args.gid, token)

    if args.notes:
        new_notes = args.notes
    elif args.preserve_body:
        new_notes = merge_notes_with_assignment(
            task.get("notes") or "",
            department=args.department,
            assignee=args.assignee,
            status=args.status,
        )
    else:
        from asana_program_common import format_assignment_header

        new_notes = format_assignment_header(
            department=args.department,
            assignee=args.assignee,
            status=args.status,
        )

    if not args.y:
        print(console_safe("--- preview notes ---"))
        print(console_safe(new_notes[:2000]))
        if input("Update? [y/N]: ").strip().lower() != "y":
            print("Cancelled.")
            return

    update_task_notes(args.gid, new_notes, token)
    print(console_safe(f"Updated notes for {args.gid} (担当: {args.assignee})"))


if __name__ == "__main__":
    main()
