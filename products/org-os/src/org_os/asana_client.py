"""Minimal Asana client for org-os epic CF operations."""
from __future__ import annotations

from typing import Any, Callable

import requests

from org_os.env import (
    assignee_type_cf_config,
    execution_order_cf_config,
    get_token,
    org_os_cf_config,
    suspend_reason_cf_config,
    task_type_cf_config,
)

ASANA_BASE = "https://app.asana.com/api/1.0"

HttpGet = Callable[..., Any]
HttpPut = Callable[..., Any]

_http_get: HttpGet = requests.get
_http_put: HttpPut = requests.put


def set_http_handlers(*, get: HttpGet | None = None, put: HttpPut | None = None) -> None:
    """Inject HTTP handlers for tests (no network)."""
    global _http_get, _http_put
    if get is not None:
        _http_get = get
    if put is not None:
        _http_put = put


def reset_http_handlers() -> None:
    """Restore default requests.get / requests.put."""
    global _http_get, _http_put
    _http_get = requests.get
    _http_put = requests.put

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
    r = _http_get(
        f"{ASANA_BASE}/tasks/{task_gid}",
        headers=_headers(token),
        params={
            "opt_fields": (
                "name,gid,completed,parent.gid,parent.name,"
                "custom_fields,custom_fields.enum_value.name,custom_fields.enum_value.gid,"
                "custom_fields.number_value"
            ),
        },
    )
    r.raise_for_status()
    return r.json().get("data") or {}


def resolve_epic_gid(task_gid: str, token: str | None = None, *, max_depth: int = 8) -> str:
    """Walk parent chain to Task Type=Epic; fallback to task_gid."""
    current = str(task_gid)
    seen: set[str] = set()
    for _ in range(max_depth):
        if current in seen:
            break
        seen.add(current)
        task = fetch_task(current, token)
        if is_watch_epic(task) or read_task_type(task) == "Epic":
            return current
        parent = (task.get("parent") or {}).get("gid")
        if not parent:
            break
        current = str(parent)
    return str(task_gid)


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


def _suspend_reason_gid_for_name(reason_name: str) -> str | None:
    cfg = suspend_reason_cf_config()
    if not cfg:
        return None
    key = (reason_name or "").strip()
    mapping = {
        "Approval": cfg.get("approval_gid"),
        "Human Review": cfg.get("human_review_gid"),
        "External Block": cfg.get("external_block_gid"),
    }
    if key in mapping and mapping[key]:
        return mapping[key]
    for label, gid in mapping.items():
        if label.strip().lower() == key.lower() and gid:
            return gid
    return None


def read_execution_order(task: dict) -> int | None:
    cfg = execution_order_cf_config()
    if not cfg:
        return None
    field_gid = cfg["field_gid"]
    for cf in task.get("custom_fields") or []:
        if str(cf.get("gid")) != field_gid:
            continue
        num = cf.get("number_value")
        if num is None:
            return None
        try:
            return int(num)
        except (TypeError, ValueError):
            return None
    return None


def read_suspend_reason(task: dict) -> str | None:
    cfg = suspend_reason_cf_config()
    if not cfg:
        return None
    field_gid = cfg["field_gid"]
    for cf in task.get("custom_fields") or []:
        if str(cf.get("gid")) != field_gid:
            continue
        enum_val = cf.get("enum_value") or {}
        name = (enum_val.get("name") or "").strip()
        return name or None
    return None


def set_suspend_reason(
    task_gid: str,
    reason_name: str | None,
    *,
    token: str | None = None,
    dry_run: bool = False,
) -> None:
    cfg = suspend_reason_cf_config()
    if not cfg:
        raise RuntimeError(
            "OS Suspend Reason CF GIDs missing — run: python tools/sync_org_os_cf_env.py --project <GID> --write -y"
        )
    field_gid = cfg["field_gid"]
    if reason_name is None or not str(reason_name).strip():
        enum_gid = None
    else:
        enum_gid = _suspend_reason_gid_for_name(str(reason_name))
        if not enum_gid:
            raise ValueError(f"unknown OS Suspend Reason {reason_name!r}")
    if dry_run:
        print(f"DRY-RUN  set_suspend_reason  task={task_gid}  reason={reason_name!r}")
        return
    custom_fields: dict[str, str | None] = {field_gid: enum_gid}
    r = _http_put(
        f"{ASANA_BASE}/tasks/{task_gid}",
        json={"data": {"custom_fields": custom_fields}},
        headers=_headers(token),
    )
    r.raise_for_status()


def set_approval_required(
    task_gid: str,
    value: str,
    *,
    token: str | None = None,
    dry_run: bool = False,
) -> None:
    """Backward-compat: set Approval Required Yes/No when CF exists."""
    cfg = org_os_cf_config()
    ap_field = cfg.get("approval_field_gid")
    if not ap_field:
        return
    yes = (value or "").strip().lower() in ("yes", "y", "true", "1")
    ap_gid = cfg.get("approval_yes_gid") if yes else cfg.get("approval_no_gid")
    if not ap_gid:
        return
    if dry_run:
        print(f"DRY-RUN  set_approval_required  task={task_gid}  value={value!r}")
        return
    r = _http_put(
        f"{ASANA_BASE}/tasks/{task_gid}",
        json={"data": {"custom_fields": {ap_field: ap_gid}}},
        headers=_headers(token),
    )
    r.raise_for_status()


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
    r = _http_put(
        f"{ASANA_BASE}/tasks/{task_gid}",
        json={"data": {"custom_fields": custom_fields}},
        headers=_headers(token),
    )
    r.raise_for_status()


def list_project_tasks(project_gid: str, *, token: str | None = None) -> list[dict]:
    r = _http_get(
        f"{ASANA_BASE}/projects/{project_gid}/tasks",
        headers=_headers(token),
        params={
            "opt_fields": "name,gid,completed,created_at,modified_at,permalink_url,custom_fields,custom_fields.enum_value.name,custom_fields.enum_value.gid"
        },
    )
    r.raise_for_status()
    return r.json().get("data") or []
