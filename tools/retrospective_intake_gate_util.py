#!/usr/bin/env python3
"""Shared helpers for epic retrospective intake gate — opt-in human approval."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

GATE_MARKER = "【承認】レトロ改善候補"
GATE_TITLE = f"{GATE_MARKER} → intake 起票"


def _env_enabled() -> bool:
    return os.environ.get("ORG_OPS_RETRO_INTAKE_GATE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _retro_enabled(retro_path: Path | None) -> bool:
    if retro_path is None or not retro_path.is_file():
        return False
    try:
        data = json.loads(retro_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return bool(data.get("human_retro_intake_gate"))


def _parent_notes_enabled(parent_gid: str | None, token: str | None) -> bool:
    if not parent_gid or not token:
        return False
    from asana_program_common import fetch_task  # noqa: WPS433

    notes = str(fetch_task(parent_gid, token).get("notes") or "")
    return bool(
        re.search(r"^human_retro_intake_gate:\s*yes\s*$", notes, re.IGNORECASE | re.MULTILINE)
    )


def _env_opt_out() -> bool:
    return os.environ.get("ORG_OPS_RETRO_INTAKE_GATE_OPT_OUT", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def retro_intake_gate_opt_out(*, cli_flag: bool = False) -> bool:
    """True when human retro gate should NOT be created (Phase 2 default-on)."""
    if cli_flag:
        return True
    return _env_opt_out()


def human_retro_intake_gate_requested(
    retro_path: Path | None = None,
    parent_gid: str | None = None,
    token: str | None = None,
    *,
    cli_flag: bool = False,
    cli_skip: bool = False,
) -> bool:
    """True when retrospective intake gate (human 【承認】) should be created."""
    if cli_skip or retro_intake_gate_opt_out():
        return False
    if cli_flag:
        return True
    if _env_enabled():
        return True
    if _retro_enabled(retro_path):
        return True
    if _parent_notes_enabled(parent_gid, token):
        return True
    return True


def find_retro_intake_gate_sub(parent_gid: str, token: str) -> dict[str, Any] | None:
    from asana_program_common import list_subtasks  # noqa: WPS433

    matches = [
        s
        for s in list_subtasks(parent_gid, token)
        if (s.get("name") or "").strip().startswith(GATE_MARKER)
    ]
    if not matches:
        return None
    incomplete = [m for m in matches if not m.get("completed")]
    if incomplete:
        return incomplete[-1]
    return matches[-1]
