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
    set_assignee_type_org_ops,
    update_task_notes,
)


def _notes_for_item(item: dict[str, Any], default_department: str) -> str:
    return assemble_subtask_notes(
        background=item.get("background", ""),
        summary=item.get("summary", ""),
        done_when=item.get("done_when", ""),
        department=item.get("department", default_department),
        assignee=item.get("assignee"),
        status=item.get("status", "assigned"),
        pillar=item.get("pillar"),
    )


def main() -> None:
    p = argparse.ArgumentParser(description="PM: create subtasks from assign plan JSON")
    p.add_argument("--parent", required=True, help="Parent task GID (e.g. 【1/7】)")
    p.add_argument("--plan", required=True, type=Path, help="JSON plan file")
    p.add_argument(
        "--department",
        default="analysis",
        help="Default チーム: header for subtasks and parent (analysis|ux|development|planning)",
    )
    p.add_argument(
        "--update-parent-assignee",
        default="analytics-pm",
        help="Set parent 担当 after creating children (e.g. ux-pm, analytics-pm)",
    )
    p.add_argument("-y", action="store_true")
    p.add_argument(
        "--skip-intake-gate",
        action="store_true",
        help="Skip development full-ui ## 依存 check (emergency only)",
    )
    args = p.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    items = plan.get("subtasks") or []
    if not items:
        print("Plan has no subtasks.", file=sys.stderr)
        sys.exit(1)

    load_env_from_dotfile()
    token = get_token()
    parent = fetch_task(args.parent, token)

    if args.department == "development" and not args.skip_intake_gate:
        repo_root = _SCRIPT_DIR.parents[4]
        tools_dir = str(repo_root / "tools")
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        from pm_intake_gate import (  # noqa: WPS433
            check_development_intake,
            format_blocked,
        )

        notes = str(parent.get("notes") or "")
        ok, failures = check_development_intake(
            notes,
            plan_profile=plan.get("profile"),
        )
        if not ok:
            print(
                format_blocked(
                    gid=args.parent,
                    tool="pm_assign_subtasks.py",
                    failures=failures,
                ),
                file=sys.stderr,
            )
            for item in failures:
                print(f"  - {item}", file=sys.stderr)
            print(
                "HINT  python tools/pm_intake_gate.py --gid "
                f"{args.parent} --plan {args.plan}",
                file=sys.stderr,
            )
            sys.exit(1)

    if not args.y:
        print(console_safe(f"Parent: {parent.get('name')} ({args.parent})"))
        print(console_safe(f"Will create {len(items)} subtask(s)."))
        if input("Continue? [y/N]: ").strip().lower() != "y":
            print("Cancelled.")
            return

    created: list[dict[str, Any]] = []
    for item in reversed(items):
        name = item["name"]
        notes = _notes_for_item(item, args.department)
        sub = create_subtask(args.parent, name, notes, token)
        sub_gid = str(sub.get("gid") or "")
        cf_ok = set_assignee_type_org_ops(sub_gid, token) if sub_gid else False
        created.append({**sub, "assignee_type_cf": cf_ok})
        cf_note = " CF=AI" if cf_ok else " CF=skip"
        print(
            console_safe(
                f"  + {sub['gid']}  {name}  → 担当: {item.get('assignee')}{cf_note}"
            )
        )

    if args.update_parent_assignee:
        notes = merge_notes_with_assignment(
            parent.get("notes") or "",
            department=args.department,
            assignee=args.update_parent_assignee,
            status="in_progress",
        )
        update_task_notes(args.parent, notes, token)
        print(console_safe(f"Parent notes → 担当: {args.update_parent_assignee}, 状態: in_progress"))
        set_assignee_type_org_ops(args.parent, token)

    out = {"parent_gid": args.parent, "created": [{"gid": t["gid"], "name": t.get("name")} for t in created]}
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
