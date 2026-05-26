"""org-os kernel syscalls — the only write path for epic OS State transitions."""
from __future__ import annotations

from org_os import asana_client
from org_os.constants import SUSPEND_REASONS
from org_os.env import require_agent_id


def start(epic_gid: str, agent_id: str | None = None, *, dry_run: bool = False) -> dict:
    """Ready → Running. Requires ORG_OS_AGENT_ID (or explicit agent_id)."""
    aid = require_agent_id(agent_id)
    task = asana_client.fetch_task(epic_gid)
    current = asana_client.read_os_state(task)
    if current != "Ready":
        raise ValueError(f"epic {epic_gid} os_state={current!r}; start requires Ready")
    asana_client.set_os_state(epic_gid, "Running", dry_run=dry_run)
    asana_client.set_suspend_reason(epic_gid, None, dry_run=dry_run)
    asana_client.set_approval_required(epic_gid, "No", dry_run=dry_run)
    return {"epic_gid": epic_gid, "os_state": "Running", "agent_id": aid}


def suspend(
    epic_gid: str,
    reason: str,
    *,
    ref: str | None = None,
    dry_run: bool = False,
) -> dict:
    """Running → Waiting + OS Suspend Reason (Asana enum display name)."""
    reason_name = (reason or "").strip()
    if reason_name not in SUSPEND_REASONS:
        raise ValueError(f"suspend reason must be one of {SUSPEND_REASONS!r}, got {reason!r}")
    task = asana_client.fetch_task(epic_gid)
    current = asana_client.read_os_state(task)
    if current not in ("Running", "Ready"):
        raise ValueError(
            f"epic {epic_gid} os_state={current!r}; suspend requires Ready or Running"
        )
    asana_client.set_os_state(epic_gid, "Waiting", dry_run=dry_run)
    asana_client.set_suspend_reason(epic_gid, reason_name, dry_run=dry_run)
    if reason_name == "Approval":
        asana_client.set_approval_required(epic_gid, "Yes", dry_run=dry_run)
    return {
        "epic_gid": epic_gid,
        "os_state": "Waiting",
        "suspend_reason": reason_name,
        "ref": ref,
    }


def resume(epic_gid: str, *, ref: str | None = None, dry_run: bool = False) -> dict:
    """Waiting → Ready; clears OS Suspend Reason."""
    task = asana_client.fetch_task(epic_gid)
    current = asana_client.read_os_state(task)
    if current != "Waiting":
        raise ValueError(f"epic {epic_gid} os_state={current!r}; resume requires Waiting")
    asana_client.set_os_state(epic_gid, "Ready", dry_run=dry_run)
    asana_client.set_suspend_reason(epic_gid, None, dry_run=dry_run)
    asana_client.set_approval_required(epic_gid, "No", dry_run=dry_run)
    return {"epic_gid": epic_gid, "os_state": "Ready", "ref": ref}


def complete(epic_gid: str, *, dry_run: bool = False) -> dict:
    """Ready / Running / Waiting → Done."""
    task = asana_client.fetch_task(epic_gid)
    current = asana_client.read_os_state(task)
    if current == "Done":
        return {"epic_gid": epic_gid, "os_state": "Done"}
    if current not in ("Ready", "Running", "Waiting"):
        raise ValueError(
            f"epic {epic_gid} os_state={current!r}; complete expects Ready, Running, or Waiting"
        )
    asana_client.set_os_state(epic_gid, "Done", dry_run=dry_run)
    asana_client.set_suspend_reason(epic_gid, None, dry_run=dry_run)
    asana_client.set_approval_required(epic_gid, "No", dry_run=dry_run)
    return {"epic_gid": epic_gid, "os_state": "Done"}


def init_epic(epic_gid: str, *, dry_run: bool = False) -> dict:
    """Bootstrap hook: Ready, no suspend reason, Approval Required=No."""
    asana_client.set_os_state(epic_gid, "Ready", dry_run=dry_run)
    asana_client.set_suspend_reason(epic_gid, None, dry_run=dry_run)
    asana_client.set_approval_required(epic_gid, "No", dry_run=dry_run)
    return {"epic_gid": epic_gid, "os_state": "Ready"}
