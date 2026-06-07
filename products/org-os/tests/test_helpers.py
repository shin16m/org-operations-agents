"""Shared env + task fixtures for org-os tests."""
from __future__ import annotations

import os
from unittest import mock


TEST_ENV = {
    "ASANA_TOKEN": "test-token",
    "ORG_OS_AGENT_ID": "workflow-orchestrator",
    "ASANA_OS_STATE_FIELD_GID": "CF_OS",
    "ASANA_OS_STATE_READY_GID": "OS_READY",
    "ASANA_OS_STATE_RUNNING_GID": "OS_RUNNING",
    "ASANA_OS_STATE_WAITING_GID": "OS_WAITING",
    "ASANA_OS_STATE_DONE_GID": "OS_DONE",
    "ASANA_APPROVAL_REQUIRED_FIELD_GID": "CF_AP",
    "ASANA_APPROVAL_REQUIRED_YES_GID": "AP_YES",
    "ASANA_APPROVAL_REQUIRED_NO_GID": "AP_NO",
    "ASANA_ASSIGNEE_TYPE_FIELD_GID": "CF_AGENT",
    "ASANA_ASSIGNEE_TYPE_AI_GID": "AG_AI",
    "ASANA_ASSIGNEE_TYPE_HUMAN_GID": "AG_HUMAN",
    "ASANA_TASK_TYPE_FIELD_GID": "CF_TT",
    "ASANA_TASK_TYPE_INTAKE_GID": "TT_INTAKE",
    "ASANA_TASK_TYPE_EPIC_GID": "TT_EPIC",
    "ASANA_OS_SUSPEND_REASON_FIELD_GID": "CF_SR",
    "ASANA_OS_SUSPEND_REASON_APPROVAL_GID": "SR_APPROVAL",
    "ASANA_OS_SUSPEND_REASON_HUMAN_REVIEW_GID": "SR_HR",
    "ASANA_OS_SUSPEND_REASON_EXTERNAL_BLOCK_GID": "SR_EXT",
}


def env_patch() -> mock._patch_dict:
    return mock.patch.dict(os.environ, TEST_ENV, clear=False)


def epic_task(
    *,
    gid: str = "EPIC1",
    os_state: str = "Ready",
    agent: str = "AI",
    task_type: str = "Epic",
    approval: str | None = "No",
    suspend_reason: str | None = None,
    created_at: str = "2026-01-01T00:00:00Z",
) -> dict:
    state_gid = {
        "Ready": "OS_READY",
        "Running": "OS_RUNNING",
        "Waiting": "OS_WAITING",
        "Done": "OS_DONE",
    }[os_state]
    agent_gid = "AG_AI" if agent == "AI" else "AG_HUMAN"
    tt_gid = "TT_EPIC" if task_type == "Epic" else "TT_INTAKE"
    cfs = [
        {"gid": "CF_OS", "enum_value": {"gid": state_gid, "name": os_state}},
        {"gid": "CF_AGENT", "enum_value": {"gid": agent_gid, "name": agent}},
        {"gid": "CF_TT", "enum_value": {"gid": tt_gid, "name": task_type}},
    ]
    if approval is not None:
        ap_gid = "AP_YES" if approval == "Yes" else "AP_NO"
        cfs.append({"gid": "CF_AP", "enum_value": {"gid": ap_gid, "name": approval}})
    if suspend_reason is not None:
        sr_gid = {
            "Approval": "SR_APPROVAL",
            "Human Review": "SR_HR",
            "External Block": "SR_EXT",
        }.get(suspend_reason, suspend_reason)
        cfs.append({"gid": "CF_SR", "enum_value": {"gid": sr_gid, "name": suspend_reason}})
    return {
        "gid": gid,
        "name": f"Epic {gid}",
        "completed": False,
        "created_at": created_at,
        "modified_at": created_at,
        "custom_fields": cfs,
    }
