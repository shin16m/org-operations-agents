#!/usr/bin/env python3
"""Create nested subtasks from PM assignment plan JSON."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    assemble_subtask_notes,
    console_safe,
    create_subtask,
    fetch_task,
    merge_notes_with_assignment,
    update_task_notes,
)


def _notes_for_item(item: dict[str, Any]) -> str:
    return assemble_subtask_notes(
        background=item.get("background", ""),
        summary=item.get("summary", ""),
        done_when=item.get("done_when", ""),
        department=item.get("department", "analysis"),
        assignee=item.get("assignee"),
        status=item.get("status", "assigned"),
        pillar=item.get("pillar"),
    )


def main() -> None:
    p = argparse.ArgumentParser(description="PM: create subtasks from assign plan JSON")
    p.add_argument("--parent", required=True, help="Parent task GID (e.g. 【1/7】)")
    p.add_argument("--plan", required=True, type=Path, help="JSON plan file")
    p.add_argument(
        "--update-parent-assignee",
        default="analytics-pm",
        help="Set parent 担当 after creating children",
    )
    p.add_argument("-y", action="store_true")
    args = p.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    items = plan.get("subtasks") or []
    if not items:
        print("Plan has no subtasks.", file=sys.stderr)
        sys.exit(1)

    load_env_from_dotfile()
    token = get_token()
    parent = fetch_task(args.parent, token)

    if not args.y:
        print(console_safe(f"Parent: {parent.get('name')} ({args.parent})"))
        print(console_safe(f"Will create {len(items)} subtask(s)."))
        if input("Continue? [y/N]: ").strip().lower() != "y":
            print("Cancelled.")
            return

    created: list[dict[str, Any]] = []
    for item in reversed(items):
        name = item["name"]
        notes = _notes_for_item(item)
        sub = create_subtask(args.parent, name, notes, token)
        created.append(sub)
        print(console_safe(f"  + {sub['gid']}  {name}  → 担当: {item.get('assignee')}"))

    if args.update_parent_assignee:
        notes = merge_notes_with_assignment(
            parent.get("notes") or "",
            department="analysis",
            assignee=args.update_parent_assignee,
            status="in_progress",
        )
        update_task_notes(args.parent, notes, token)
        print(console_safe(f"Parent notes → 担当: {args.update_parent_assignee}, 状態: in_progress"))

    out = {"parent_gid": args.parent, "created": [{"gid": t["gid"], "name": t.get("name")} for t in created]}
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
