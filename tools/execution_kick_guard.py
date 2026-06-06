#!/usr/bin/env python3
"""Guard execution L3b / PM kicks until epic is Running and planning is done."""
from __future__ import annotations

from typing import Any

GATE_MARKERS = ("【承認】", "【レビュー】")


def _infer_planning_incomplete(epic_gid: str, token: str) -> str | None:
    from asana_program_common import fetch_task, list_subtasks, parse_task_assignment  # noqa: WPS433
    from dispatch_prompt_util import infer_department, load_organizations  # noqa: WPS433

    pillar_defaults = load_organizations().get("pillar_defaults")
    for sub in list_subtasks(epic_gid, token):
        if sub.get("completed"):
            continue
        name = str(sub.get("name") or "")
        if name.startswith(GATE_MARKERS):
            continue
        gid = str(sub.get("gid") or "")
        notes = str(fetch_task(gid, token).get("notes") or "")
        dept = infer_department(
            notes=notes,
            title=name,
            pillar_defaults=pillar_defaults,
        )
        if dept == "planning":
            return gid
        assignee = parse_task_assignment(notes).get("assignee")
        if assignee == "planning-pm" and "企画" in name:
            return gid
    return None


def execution_kick_allowed(
    epic_gid: str,
    token: str,
    *,
    require_running: bool = True,
    require_planning_complete: bool = True,
) -> tuple[bool, str]:
    """Return (allowed, reason). reason is ok or BLOCKED detail."""
    from org_os import asana_client  # noqa: WPS433

    task = asana_client.fetch_task(epic_gid, token)
    state = asana_client.read_os_state(task) or ""
    if require_running and state != "Running":
        return False, f"epic_state={state or 'unknown'}"

    if require_planning_complete:
        open_planning = _infer_planning_incomplete(epic_gid, token)
        if open_planning:
            return False, f"planning_child_open={open_planning}"

    return True, "ok"


def log_blocked(*, epic_gid: str, tool: str, reason: str) -> None:
    from asana_program_common import console_safe  # noqa: WPS433

    print(
        console_safe(
            f"BLOCKED  execution_kick  epic={epic_gid}  tool={tool}  reason={reason}"
        )
    )


def resolve_epic_for_pm_child(pm_child_gid: str, token: str) -> str:
    from org_os.asana_client import resolve_epic_gid  # noqa: WPS433

    return resolve_epic_gid(pm_child_gid, token)
