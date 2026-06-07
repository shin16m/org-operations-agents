#!/usr/bin/env python3
"""Shared helpers for L2 execution dispatch human-confirm gate (opt-in)."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


def _env_enabled() -> bool:
    return os.environ.get("ORG_OPS_EXECUTION_DISPATCH_CONFIRM", "").strip().lower() in (
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
    return bool(meta.get("human_execution_dispatch"))


def _epic_notes_enabled(epic_gid: str | None, token: str | None) -> bool:
    if not epic_gid or not token:
        return False
    from asana_program_common import fetch_task  # noqa: WPS433

    notes = str(fetch_task(epic_gid, token).get("notes") or "")
    return bool(re.search(r"human_execution_dispatch:\s*yes\b", notes, re.IGNORECASE))


def human_execution_dispatch_requested(
    handoff_path: Path | None = None,
    epic_gid: str | None = None,
    token: str | None = None,
    *,
    cli_flag: bool = False,
) -> bool:
    """True when L2 dispatch should wait for human chat confirm before task-dispatcher."""
    if cli_flag:
        return True
    if _env_enabled():
        return True
    if _handoff_enabled(handoff_path):
        return True
    if _epic_notes_enabled(epic_gid, token):
        return True
    return False
