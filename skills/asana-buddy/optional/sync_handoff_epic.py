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
    Path(__file__).resolve().parents[2]
    / "issue-story-planner"
    / "examples"
    / "handoff.agent-workflow-orchestration.json"
)
DEFAULT_PARENT = "1214879346897459"

# Order matters: first match wins; index = subtasks[] position
# More specific patterns first (avoid "1/11" matching inside "11/11", "1/5" in "11/5" N/A)
MATCH_RULES: list[tuple[str, int]] = [
    (r"5/5", 4),
    (r"4/5", 3),
    (r"3/5", 2),
    (r"2/5", 1),
    (r"1/5", 0),
    (r"11/11", 10),
    (r"10/11", 9),
    (r"9/11", 8),
    (r"8/11", 7),
    (r"7/11", 6),
    (r"6/11", 5),
    (r"5/11", 4),
    (r"4/11", 3),
    (r"3/11", 2),
    (r"2/11", 1),
    (r"1/11", 0),
]


def match_index(name: str) -> int | None:
    for pat, idx in MATCH_RULES:
        if re.search(pat, name):
            return idx
    return None


def complete_subtasks(parent_gid: str, token: str, through: int | None = None) -> None:
    """Mark subtasks 1..through (1-based) completed by title match."""
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{ASANA_BASE}/tasks/{parent_gid}/subtasks",
        headers=headers,
        params={"opt_fields": "name,completed"},
    )
    r.raise_for_status()
    for t in r.json()["data"]:
        idx = match_index(t["name"])
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
        help="Mark subtasks 1..N completed (by n/5 or n/11 title match)",
    )
    p.add_argument(
        "--complete-only",
        action="store_true",
        help="Only run --complete-through, skip notes sync",
    )
    args = p.parse_args()

    handoff = json.loads(Path(args.handoff).read_text(encoding="utf-8"))
    expected = handoff["subtasks"]

    load_env_from_dotfile()
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    if args.dry_run:
        print("dry-run parent", args.parent, "subtasks", len(expected))
        return

    if args.complete_through is not None:
        complete_subtasks(args.parent, token, args.complete_through)

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
        idx = match_index(t["name"])
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
