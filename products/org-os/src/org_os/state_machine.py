"""Epic OS state transitions."""
from __future__ import annotations

from org_os import asana_client


def status_epic(epic_gid: str) -> dict:
    task = asana_client.fetch_task(epic_gid)
    return {
        "gid": epic_gid,
        "name": task.get("name"),
        "completed": task.get("completed"),
        "os_state": asana_client.read_os_state(task),
        "approval_required": asana_client.read_approval_required(task),
    }


def dispatch_epic(epic_gid: str, *, dry_run: bool = False) -> str:
    """Ready → Running. Returns new state name."""
    task = asana_client.fetch_task(epic_gid)
    current = asana_client.read_os_state(task)
    if current != "Ready":
        raise ValueError(f"epic {epic_gid} os_state={current!r}; dispatch requires Ready")
    asana_client.set_os_state(epic_gid, "Running", dry_run=dry_run)
    return "Running"


def complete_epic(epic_gid: str, *, dry_run: bool = False) -> str:
    """Transition epic OS State to Done (Ready, Running, or Waiting)."""
    task = asana_client.fetch_task(epic_gid)
    current = asana_client.read_os_state(task)
    if current == "Done":
        return "Done"
    if current not in ("Ready", "Running", "Waiting"):
        raise ValueError(
            f"epic {epic_gid} os_state={current!r}; complete expects Ready, Running, or Waiting"
        )
    asana_client.set_os_state(epic_gid, "Done", dry_run=dry_run)
    return "Done"


def need_approval(epic_gid: str, *, dry_run: bool = False) -> str:
    """Running → Waiting (Approval Required CF は org-ops 側が別途設定)."""
    task = asana_client.fetch_task(epic_gid)
    current = asana_client.read_os_state(task)
    if current != "Running":
        raise ValueError(f"epic {epic_gid} os_state={current!r}; need_approval requires Running")
    asana_client.set_os_state(epic_gid, "Waiting", dry_run=dry_run)
    return "Waiting"


def approval_done(epic_gid: str, *, dry_run: bool = False) -> str:
    """Waiting → Ready."""
    task = asana_client.fetch_task(epic_gid)
    current = asana_client.read_os_state(task)
    if current != "Waiting":
        raise ValueError(f"epic {epic_gid} os_state={current!r}; approval_done requires Waiting")
    asana_client.set_os_state(epic_gid, "Ready", dry_run=dry_run)
    return "Ready"
