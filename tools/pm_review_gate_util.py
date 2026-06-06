#!/usr/bin/env python3
"""Shared helpers for PM assign-review gate (opt-in human review)."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

GATE_MARKER = "【レビュー】"
GATE_TITLE = f"{GATE_MARKER}サブ構成・担当割り当て"


def _env_enabled() -> bool:
    return os.environ.get("ORG_OPS_PM_REVIEW_GATE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _plan_enabled(plan_path: Path | None) -> bool:
    if plan_path is None or not plan_path.is_file():
        return False
    try:
        data = json.loads(plan_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return bool(data.get("human_review_gate"))


def _parent_notes_enabled(parent_gid: str | None, token: str | None) -> bool:
    if not parent_gid or not token:
        return False
    from asana_program_common import fetch_task  # noqa: WPS433

    notes = str(fetch_task(parent_gid, token).get("notes") or "")
    return bool(re.search(r"human_review_gate:\s*yes\b", notes, re.IGNORECASE))


def human_review_gate_requested(
    plan_path: Path | None = None,
    parent_gid: str | None = None,
    token: str | None = None,
    *,
    cli_flag: bool = False,
) -> bool:
    """True when PM assign-review gate (human 【レビュー】) should be created."""
    if cli_flag:
        return True
    if _env_enabled():
        return True
    if _plan_enabled(plan_path):
        return True
    if _parent_notes_enabled(parent_gid, token):
        return True
    return False


def is_pm_assign_review_gate_name(name: str) -> bool:
    text = (name or "").strip()
    return text.startswith(GATE_MARKER) and "サブ構成" in text


def find_pm_assign_review_gate_sub(
    parent_gid: str,
    token: str,
) -> dict[str, Any] | None:
    from asana_program_common import list_subtasks  # noqa: WPS433

    matches = [
        s
        for s in list_subtasks(parent_gid, token)
        if is_pm_assign_review_gate_name(str(s.get("name") or ""))
    ]
    if not matches:
        return None
    incomplete = [m for m in matches if not m.get("completed")]
    if incomplete:
        return incomplete[-1]
    return matches[-1]
