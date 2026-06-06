#!/usr/bin/env python3
"""Shared helpers for planning gate (handoff_approved) — opt-in human approval."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

GATE_MARKER = "【承認】"
GATE_TITLE_SUFFIX = "Handoff 承認"
GATE_TITLE = f"{GATE_MARKER}{GATE_TITLE_SUFFIX}"
RETRO_GATE_MARKER = "【承認】レトロ改善候補"


def _env_enabled() -> bool:
    return os.environ.get("ORG_OPS_PLANNING_APPROVAL_GATE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _handoff_enabled(handoff_path: Path | None) -> bool:
    if handoff_path is None or not handoff_path.is_file():
        return False
    try:
        data = json.loads(handoff_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    meta = data.get("meta") or {}
    return bool(meta.get("human_planning_approval"))


def _parent_notes_enabled(parent_gid: str | None, token: str | None) -> bool:
    if not parent_gid or not token:
        return False
    from asana_program_common import fetch_task  # noqa: WPS433

    notes = str(fetch_task(parent_gid, token).get("notes") or "")
    return bool(
        re.search(r"^human_planning_approval:\s*yes\s*$", notes, re.IGNORECASE | re.MULTILINE)
    )


def human_planning_approval_requested(
    handoff_path: Path | None = None,
    parent_gid: str | None = None,
    token: str | None = None,
    *,
    cli_flag: bool = False,
) -> bool:
    """True when planning gate (human 【承認】) should be created."""
    if cli_flag:
        return True
    if _env_enabled():
        return True
    if _handoff_enabled(handoff_path):
        return True
    if _parent_notes_enabled(parent_gid, token):
        return True
    return False


def is_planning_approval_gate_name(name: str) -> bool:
    text = (name or "").strip()
    if text.startswith(RETRO_GATE_MARKER):
        return False
    return text.startswith(GATE_MARKER) and "Handoff" in text


def find_planning_approval_gate_sub(
    parent_gid: str,
    token: str,
) -> dict[str, Any] | None:
    from asana_program_common import list_subtasks  # noqa: WPS433

    matches = [
        s
        for s in list_subtasks(parent_gid, token)
        if is_planning_approval_gate_name(str(s.get("name") or ""))
    ]
    if not matches:
        return None
    incomplete = [m for m in matches if not m.get("completed")]
    if incomplete:
        return incomplete[-1]
    return matches[-1]
