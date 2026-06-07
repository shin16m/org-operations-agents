"""Scan legacy epics missing OS State for backfill."""
from __future__ import annotations

from dataclasses import dataclass

from org_os import asana_client

VALID_OS_STATES = frozenset({"Ready", "Running", "Waiting", "Done"})


@dataclass(frozen=True)
class EpicBackfillRow:
    gid: str
    name: str
    os_state: str | None
    task_type: str | None
    completed: bool
    action: str  # init | ok | warn | skip
    reason: str


@dataclass
class BackfillScan:
    project_gid: str
    rows: list[EpicBackfillRow]

    @property
    def init_candidates(self) -> list[EpicBackfillRow]:
        return [r for r in self.rows if r.action == "init"]

    @property
    def warnings(self) -> list[EpicBackfillRow]:
        return [r for r in self.rows if r.action == "warn"]


def _classify_epic(task: dict) -> EpicBackfillRow:
    gid = str(task.get("gid") or "")
    name = (task.get("name") or "")[:80]
    completed = bool(task.get("completed"))
    task_type = asana_client.read_task_type(task)
    os_state = asana_client.read_os_state(task)

    if task_type != "Epic":
        return EpicBackfillRow(
            gid, name, os_state, task_type, completed, "skip", "not Task Type=Epic"
        )
    if completed:
        return EpicBackfillRow(
            gid, name, os_state, task_type, completed, "skip", "completed epic"
        )
    if not os_state:
        return EpicBackfillRow(
            gid, name, os_state, task_type, completed, "init", "OS State unset"
        )
    if os_state in VALID_OS_STATES:
        return EpicBackfillRow(
            gid, name, os_state, task_type, completed, "ok", f"os_state={os_state}"
        )
    return EpicBackfillRow(
        gid,
        name,
        os_state,
        task_type,
        completed,
        "warn",
        f"unexpected os_state={os_state!r}",
    )


def scan_project(
    project_gid: str,
    *,
    epic_gid: str | None = None,
    include_completed: bool = False,
    token: str | None = None,
) -> BackfillScan:
    if epic_gid:
        task = asana_client.fetch_task(epic_gid, token)
        row = _classify_epic(task)
        if row.action == "skip" and row.reason == "completed epic" and include_completed:
            row = EpicBackfillRow(
                row.gid,
                row.name,
                row.os_state,
                row.task_type,
                row.completed,
                "init" if not row.os_state else row.action,
                row.reason,
            )
        return BackfillScan(project_gid, [row])

    tasks = asana_client.list_project_tasks(project_gid, token=token)
    rows: list[EpicBackfillRow] = []
    for task in tasks:
        row = _classify_epic(task)
        if row.action == "skip" and row.reason == "completed epic" and include_completed:
            if not row.os_state:
                row = EpicBackfillRow(
                    row.gid,
                    row.name,
                    row.os_state,
                    row.task_type,
                    row.completed,
                    "init",
                    "OS State unset (completed)",
                )
        rows.append(row)
    rows.sort(key=lambda r: r.gid)
    return BackfillScan(project_gid, rows)
