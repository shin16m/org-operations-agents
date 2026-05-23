#!/usr/bin/env python3
"""Create or sync Asana epic + subtasks from AsanaBuddyHandoff JSON (v1.1 / v1.2).

Usage:
  python handoff_to_asana.py --handoff handoff.json --list-projects
  python handoff_to_asana.py --handoff handoff.json --require-review-result review.json -y
  python handoff_to_asana.py --handoff handoff.json -y --if-not-exists
  python handoff_to_asana.py --handoff handoff.json -y --parent <PARENT_GID>
  python handoff_to_asana.py --handoff handoff.json -y --if-not-exists --dry-run
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_handler_asana import add_task_to_section, create_task, get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    console_safe,
    create_subtasks_reversed,
    find_project_task_by_exact_name,
    handoff_subtask_notes,
    list_accessible_projects,
    load_handoff,
    load_review_result,
    resolve_project_with_fallback,
    resolve_section_id,
    sync_handoff_to_parent,
)


def _print_sync_result(result: dict) -> None:
    if result.get("dry_run"):
        print(
            "dry-run sync",
            f"parent={result['parent_gid']}",
            f"update_parent={result.get('would_update_parent')}",
            f"subtasks={result.get('subtask_count')}",
        )
        return
    if result.get("updated_parent"):
        print("updated_parent", result["parent_gid"])
    for item in result.get("updated", []):
        print("updated_subtask", item["index"], item["gid"], console_safe(item["title"][:50]))
    for item in result.get("fuzzy_matched", []):
        print("fuzzy_matched", item["index"], item["gid"], item.get("department"), console_safe(item["title"][:50]))
    for item in result.get("created", []):
        print("created_subtask", item["index"], item["gid"], console_safe(item["title"][:50]))
    for item in result.get("unmatched_asana", []):
        print("unmatched_asana", item["gid"], console_safe(item["name"][:50]))


def main() -> None:
    p = argparse.ArgumentParser(description="Import or sync AsanaBuddyHandoff JSON into Asana")
    p.add_argument("--handoff", required=True, help="Path to handoff JSON file")
    p.add_argument("--project", default=None, help="Asana project GID (create mode only)")
    p.add_argument("--parent", default=None, help="Existing parent epic GID (sync mode)")
    p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    p.add_argument("--list-projects", action="store_true", help="List projects and exit")
    p.add_argument("--dry-run", action="store_true", help="Print plan only")
    p.add_argument(
        "--if-not-exists",
        action="store_true",
        help="If epic.title exists in project, sync to that parent instead of creating",
    )
    p.add_argument(
        "--require-review-result",
        metavar="PATH",
        default=None,
        help="Require PlanReviewResult JSON with status passed or passed_with_notes",
    )
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()

    if args.list_projects:
        list_accessible_projects(token)
        return

    if args.require_review_result:
        review = load_review_result(args.require_review_result)
        print("review_ok", review.get("status"))

    data = load_handoff(args.handoff)
    epic = data["epic"]
    subtasks = data["subtasks"]
    epic_title = epic["title"].strip()

    parent_gid = args.parent

    if args.if_not_exists and not parent_gid:
        project_id = resolve_project_with_fallback(args.project)
        existing = find_project_task_by_exact_name(project_id, epic_title, token)
        if existing:
            parent_gid = existing

    if parent_gid:
        if args.dry_run:
            _print_sync_result(
                sync_handoff_to_parent(parent_gid, data, token, dry_run=True)
            )
            return
        if not args.yes:
            print(f"Sync handoff to existing parent {parent_gid}? (y/N): ", end="")
            if input().strip().lower() != "y":
                print("abort")
                sys.exit(0)
        result = sync_handoff_to_parent(parent_gid, data, token)
        print("synced_existing", parent_gid)
        _print_sync_result(result)
        return

    project_id = resolve_project_with_fallback(args.project)
    section_id = resolve_section_id(None)

    if args.dry_run:
        section_note = f" section_gid={section_id}" if section_id else ""
        print(
            console_safe(
                f"dry-run: would create 1 parent + {len(subtasks)} subtasks "
                f"project_gid={project_id}{section_note} epic={epic_title!r}"
            )
        )
        return

    if not args.yes:
        print(
            f"Create 1 parent + {len(subtasks)} subtasks in {project_id}? (y/N): ",
            end="",
        )
        if input().strip().lower() != "y":
            print("abort")
            sys.exit(0)

    created = create_task(project_id, epic_title, epic["notes_markdown"], token)
    print("created_parent", created.get("gid"), created.get("permalink_url", ""))

    if section_id:
        add_task_to_section(section_id, created["gid"], token)
        print("added_to_section", section_id)

    create_subtasks_reversed(
        created["gid"],
        subtasks,
        token,
        notes_for_item=handoff_subtask_notes,
    )


if __name__ == "__main__":
    main()
