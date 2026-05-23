#!/usr/bin/env python3
"""Update Asana epic + subtasks from a Handoff JSON (no create; updates by title match)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import requests

from agent_handler_asana import ASANA_BASE, get_token, load_env_from_dotfile
from asana_program_common import load_handoff, parse_subtask_index, sync_handoff_to_parent

DEFAULT_HANDOFF = (
    Path(__file__).resolve().parents[3]
    / "planning"
    / "issue-story-planner"
    / "examples"
    / "handoff.agent-workflow-orchestration.json"
)
DEFAULT_PARENT = "1214879346897459"


def complete_subtasks(
    parent_gid: str,
    token: str,
    through: int | None = None,
    expected_count: int | None = None,
) -> None:
    """Mark subtasks 1..through (1-based) completed by title match."""
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{ASANA_BASE}/tasks/{parent_gid}/subtasks",
        headers=headers,
        params={"opt_fields": "name,completed"},
    )
    r.raise_for_status()
    for t in r.json()["data"]:
        idx = parse_subtask_index(t["name"], expected_count)
        if idx is None:
            continue
        n = idx + 1
        if through is not None and n > through:
            continue
        if t.get("completed"):
            print("already_completed", n)
            continue
        requests.put(
            f"{ASANA_BASE}/tasks/{t['gid']}",
            json={"data": {"completed": True}},
            headers=headers,
        ).raise_for_status()
        print("completed", n, t["name"][:50])


def main() -> None:
    p = argparse.ArgumentParser(description="Sync Handoff JSON to existing Asana epic subtasks")
    p.add_argument("--handoff", default=str(DEFAULT_HANDOFF))
    p.add_argument("--parent", default=DEFAULT_PARENT)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument(
        "--complete-through",
        type=int,
        default=None,
        help="Mark subtasks 1..N completed (match 【n/m】 in title)",
    )
    p.add_argument(
        "--complete-only",
        action="store_true",
        help="Only run --complete-through, skip notes sync",
    )
    args = p.parse_args()

    handoff = load_handoff(args.handoff)
    expected_count = len(handoff["subtasks"])

    load_env_from_dotfile()
    token = get_token()

    if args.dry_run:
        sync_handoff_to_parent(args.parent, handoff, token, dry_run=True)
        print("dry-run parent", args.parent, "subtasks", expected_count)
        return

    if args.complete_through is not None:
        complete_subtasks(args.parent, token, args.complete_through, expected_count)

    if args.complete_only:
        print("complete-only done")
        return

    result = sync_handoff_to_parent(args.parent, handoff, token)
    print("synced", args.parent)
    for item in result.get("updated", []):
        print("updated", item["index"], item["gid"])
    for item in result.get("fuzzy_matched", []):
        print("fuzzy_matched", item["index"], item["gid"])
    for item in result.get("created", []):
        print("created", item["index"], item["gid"])


if __name__ == "__main__":
    main()
