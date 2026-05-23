#!/usr/bin/env python3
"""Update Asana epic + subtasks from a Handoff JSON (no create; updates by title match)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import requests

from agent_handler_asana import ASANA_BASE, get_token, load_env_from_dotfile
from asana_program_common import create_subtask, handoff_subtask_notes

DEFAULT_HANDOFF = (
    Path(__file__).resolve().parents[3]
    / "planning"
    / "issue-story-planner"
    / "examples"
    / "handoff.agent-workflow-orchestration.json"
)
DEFAULT_PARENT = "1214879346897459"

# 【n/m】 in title → 0-based index (n - 1). Validates total against handoff length when given.
_SUBTASK_BRACKET_RE = re.compile(r"【\s*(\d+)\s*/\s*(\d+)\s*")


def parse_subtask_index(name: str, expected_count: int | None = None) -> int | None:
    """Return 0-based subtasks[] index from title, or None if not matched / invalid."""
    m = _SUBTASK_BRACKET_RE.search(name)
    if not m:
        return None
    n_s, total_s = m.group(1), m.group(2)
    n, total = int(n_s), int(total_s)
    if n < 1 or total < 1 or n > total:
        return None
    if expected_count is not None and total != expected_count:
        return None
    return n - 1


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

    handoff = json.loads(Path(args.handoff).read_text(encoding="utf-8"))
    expected = handoff["subtasks"]
    expected_count = len(expected)

    load_env_from_dotfile()
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    if args.dry_run:
        print("dry-run parent", args.parent, "subtasks", expected_count)
        return

    if args.complete_through is not None:
        complete_subtasks(args.parent, token, args.complete_through, expected_count)

    if args.complete_only:
        print("complete-only done")
        return

    requests.put(
        f"{ASANA_BASE}/tasks/{args.parent}",
        json={"data": {"notes": handoff["epic"]["notes_markdown"]}},
        headers=headers,
    ).raise_for_status()
    print("updated_parent", args.parent)

    r = requests.get(
        f"{ASANA_BASE}/tasks/{args.parent}/subtasks",
        headers=headers,
        params={"opt_fields": "name"},
    )
    r.raise_for_status()
    asana_tasks = r.json()["data"]

    used: set[int] = set()
    for t in asana_tasks:
        idx = parse_subtask_index(t["name"], expected_count)
        if idx is None:
            print("unmatched", t["gid"], t["name"][:60])
            continue
        if idx in used:
            print("duplicate_skip", t["gid"], t["name"][:60])
            continue
        used.add(idx)
        st = expected[idx]
        requests.put(
            f"{ASANA_BASE}/tasks/{t['gid']}",
            json={"data": {"name": st["title"], "notes": handoff_subtask_notes(st)}},
            headers=headers,
        ).raise_for_status()
        print("updated", idx + 1, st["title"][:55])

    for idx, st in enumerate(expected):
        if idx in used:
            continue
        created = create_subtask(args.parent, st["title"], handoff_subtask_notes(st), token)
        print("created", idx + 1, created.get("gid"), st["title"][:55])

    print("done mapped", len(used), "created", len(expected) - len(used))


if __name__ == "__main__":
    main()
