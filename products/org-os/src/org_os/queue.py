"""Read-only epic queues backed by Asana (SSOT)."""
from __future__ import annotations

from org_os import asana_client


def _epic_row(task: dict) -> dict:
    return {
        "epic_gid": str(task.get("gid") or ""),
        "name": task.get("name") or "",
        "created_at": task.get("created_at"),
        "modified_at": task.get("modified_at"),
        "permalink_url": task.get("permalink_url"),
        "os_state": asana_client.read_os_state(task),
        "suspend_reason": asana_client.read_suspend_reason(task),
    }


def ready_queue(project_gid: str, *, token: str | None = None) -> list[dict]:
    """Ready epics (Agent Type=AI · Task Type=Epic), FIFO by created_at ASC."""
    tasks = list_project_tasks(project_gid, token=token)
    rows: list[dict] = []
    for task in tasks:
        if not asana_client.is_watch_epic(task):
            continue
        if asana_client.read_os_state(task) != "Ready":
            continue
        ap = asana_client.read_approval_required(task)
        if ap == "Yes":
            continue
        rows.append(_epic_row(task))
    rows.sort(key=lambda r: r.get("created_at") or "")
    return rows


def wait_list(project_gid: str, *, token: str | None = None) -> list[dict]:
    """Waiting epics for dashboard / monitoring."""
    tasks = list_project_tasks(project_gid, token=token)
    rows: list[dict] = []
    for task in tasks:
        if not asana_client.is_watch_epic(task):
            continue
        if asana_client.read_os_state(task) != "Waiting":
            continue
        row = _epic_row(task)
        row["suspended_at"] = task.get("modified_at")
        rows.append(row)
    rows.sort(key=lambda r: r.get("suspended_at") or "")
    return rows


def list_project_tasks(project_gid: str, *, token: str | None = None) -> list[dict]:
    return asana_client.list_project_tasks(project_gid, token=token)
