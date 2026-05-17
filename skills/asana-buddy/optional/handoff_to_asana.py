#!/usr/bin/env python3
"""Create Asana epic + subtasks from issue-story-planner AsanaBuddyHandoff JSON (v1.1).

Usage:
  python handoff_to_asana.py --handoff ../issue-story-planner/examples/handoff.example.json --list-projects
  python handoff_to_asana.py --handoff handoff.json --require-review-result review.json -y --dry-run
  python handoff_to_asana.py --handoff handoff.json --require-review-result review.json -y --if-not-exists
  python handoff_to_asana.py --handoff handoff.json -y --project <GID>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_handler_asana import create_task, get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    console_safe,
    create_subtasks_reversed,
    find_project_task_by_exact_name,
    handoff_subtask_notes,
    list_accessible_projects,
    load_handoff,
    load_review_result,
    resolve_project_with_fallback,
)


def main() -> None:
    p = argparse.ArgumentParser(description="Import AsanaBuddyHandoff v1.1 JSON into Asana")
    p.add_argument("--handoff", required=True, help="Path to handoff JSON file")
    p.add_argument("--project", default=None, help="Asana project GID")
    p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    p.add_argument("--list-projects", action="store_true", help="List projects and exit")
    p.add_argument("--dry-run", action="store_true", help="Print plan only")
    p.add_argument(
        "--if-not-exists",
        action="store_true",
        help="Skip if epic.title already exists as top-level project task",
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

    project_id = resolve_project_with_fallback(args.project)

    if args.if_not_exists:
        existing = find_project_task_by_exact_name(project_id, epic_title, token)
        if existing:
            print(f"skip: epic already exists gid={existing}")
            return

    if args.dry_run:
        print(
            console_safe(
                f"dry-run: would create 1 parent + {len(subtasks)} subtasks "
                f"project_gid={project_id} epic={epic_title!r}"
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

    create_subtasks_reversed(
        created["gid"],
        subtasks,
        token,
        notes_for_item=handoff_subtask_notes,
    )


if __name__ == "__main__":
    main()
