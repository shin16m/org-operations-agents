"""Epic OS state transitions (legacy aliases — prefer org_os.syscall)."""
from __future__ import annotations

from org_os import asana_client
from org_os import syscall


def status_epic(epic_gid: str) -> dict:
    task = asana_client.fetch_task(epic_gid)
    return {
        "gid": epic_gid,
        "name": task.get("name"),
        "completed": task.get("completed"),
        "os_state": asana_client.read_os_state(task),
        "approval_required": asana_client.read_approval_required(task),
        "suspend_reason": asana_client.read_suspend_reason(task),
    }


def dispatch_epic(epic_gid: str, *, dry_run: bool = False, agent_id: str | None = None) -> str:
    """Ready → Running. Returns new state name."""
    result = syscall.start(epic_gid, agent_id, dry_run=dry_run)
    return result["os_state"]


def complete_epic(epic_gid: str, *, dry_run: bool = False) -> str:
    result = syscall.complete(epic_gid, dry_run=dry_run)
    return result["os_state"]


def need_approval(
    epic_gid: str,
    *,
    reason: str = "Approval",
    ref: str | None = None,
    dry_run: bool = False,
) -> str:
    result = syscall.suspend(epic_gid, reason, ref=ref, dry_run=dry_run)
    return result["os_state"]


def approval_done(epic_gid: str, *, ref: str | None = None, dry_run: bool = False) -> str:
    result = syscall.resume(epic_gid, ref=ref, dry_run=dry_run)
    return result["os_state"]
