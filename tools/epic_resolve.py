#!/usr/bin/env python3
"""Resolve org-os epic GID from any task in the epic tree."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
ORG_OS_SRC = ROOT / "products/org-os/src"
for p in (ASANA_OPT, ORG_OS_SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from org_os.asana_client import resolve_epic_gid  # noqa: E402

EXECUTION_DEPARTMENTS = frozenset(
    {"development", "ux", "analysis", "governance", "audit"}
)


def find_open_planning_child(parent_gid: str, token: str) -> str | None:
    from asana_program_common import list_subtasks, parse_task_assignment  # noqa: E402

    for sub in list_subtasks(parent_gid, token):
        if sub.get("completed"):
            continue
        dept = parse_task_assignment(sub.get("notes") or "").get("department")
        if dept == "planning":
            return str(sub.get("gid") or "")
    return None


def epic_has_execution_children(parent_gid: str, token: str) -> bool:
    from asana_program_common import list_subtasks, parse_task_assignment  # noqa: E402

    for sub in list_subtasks(parent_gid, token):
        dept = parse_task_assignment(sub.get("notes") or "").get("department")
        if dept in EXECUTION_DEPARTMENTS:
            return True
    return False
