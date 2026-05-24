"""Minimal Asana client for org-os epic CF operations."""
from __future__ import annotations

import requests

from org_os.env import assignee_type_cf_config, get_token, org_os_cf_config, task_type_cf_config

ASANA_BASE = "https://app.asana.com/api/1.0"

STATE_BY_GID: dict[str, str] = {}
GIDS_BY_STATE: dict[str, str] = {}


def _headers(token: str | None = None) -> dict[str, str]:
    return {"Authorization": f"Bearer {token or get_token()}"}


def _refresh_state_maps(cfg: dict[str, str]) -> None:
    global STATE_BY_GID, GIDS_BY_STATE
    GIDS_BY_STATE = {
        "Ready": cfg["ready_gid"],
        "Running": cfg["running_gid"],
        "Waiting": cfg["waiting_gid"],
        "Done": cfg["done_gid"],
    }
    STATE_BY_GID = {v: k for k, v in GIDS_BY_STATE.items() if v}


def _read_enum_cf(task: dict, field_gid: str, *, gid_labels: dict[str, str]) -> str | None:
    for cf in task.get("custom_fields") or []:
        if str(cf.get("gid")) != field_gid:
            continue
        enum_val = cf.get("enum_value") or {}
        gid = str(enum_val.get("gid") or "")
        if gid in gid_labels:
            return gid_labels[gid]
        name = (enum_val.get("name") or "").strip()
        return name or None
    return None


def fetch_task(task_gid: str, token: str | None = None) -> dict:
    r = requests.get(
        f"{ASANA_BASE}/tasks/{task_gid}",
        headers=_headers(token),
        params={"opt_fields": "name,gid,completed,custom_fields,custom_fields.enum_value.name,custom_fields.enum_value.gid"},
    )
    r.raise_for_status()
    return r.json().get("data") or {}


def read_os_state(task: dict) -> str | None:
    cfg = org_os_cf_config()
    _refresh_state_maps(cfg)
    field_gid = cfg["os_state_field_gid"]
    for cf in task.get("custom_fields") or []:
        if str(cf.get("gid")) != field_gid:
            continue
        enum_val = cf.get("enum_value") or {}
        gid = str(enum_val.get("gid") or "")
        return STATE_BY_GID.get(gid) or enum_val.get("name")
    return None


def read_agent_type(task: dict) -> str | None:
    cfg = assignee_type_cf_config()
    return _read_enum_cf(
        task,
        cfg["field_gid"],
        gid_labels={cfg["ai_gid"]: "AI", cfg["human_gid"]: "human"},
    )


def read_task_type(task: dict) -> str | None:
    cfg = task_type_cf_config()
    return _read_enum_cf(
        task,
        cfg["field_gid"],
        gid_labels={cfg["intake_gid"]: "Intake", cfg["epic_gid"]: "Epic"},
    )


def is_watch_epic(task: dict) -> bool:
    """org-os watch target: Agent Type=AI and Task Type=Epic."""
    if task.get("completed"):
        return False
    agent = read_agent_type(task)
    task_type = read_task_type(task)
    return agent == "AI" and task_type == "Epic"


def read_approval_required(task: dict) -> str | None:
    cfg = org_os_cf_config()
    field_gid = cfg.get("approval_field_gid")
    if not field_gid:
        return None
    for cf in task.get("custom_fields") or []:
        if str(cf.get("gid")) != field_gid:
            continue
        enum_val = cf.get("enum_value") or {}
        return enum_val.get("name")
    return None


def set_os_state(task_gid: str, state: str, *, token: str | None = None, dry_run: bool = False) -> None:
    cfg = org_os_cf_config()
    _refresh_state_maps(cfg)
    enum_gid = GIDS_BY_STATE.get(state)
    if not enum_gid:
        raise ValueError(f"unknown state {state!r}")
    if dry_run:
        print(f"DRY-RUN  set_os_state  task={task_gid}  state={state}")
        return
    custom_fields = {cfg["os_state_field_gid"]: enum_gid}
    r = requests.put(
        f"{ASANA_BASE}/tasks/{task_gid}",
        json={"data": {"custom_fields": custom_fields}},
        headers=_headers(token),
    )
    r.raise_for_status()


def list_project_tasks(project_gid: str, *, token: str | None = None) -> list[dict]:
    r = requests.get(
        f"{ASANA_BASE}/projects/{project_gid}/tasks",
        headers=_headers(token),
        params={"opt_fields": "name,gid,completed,custom_fields,custom_fields.enum_value.name,custom_fields.enum_value.gid"},
    )
    r.raise_for_status()
    return r.json().get("data") or []
