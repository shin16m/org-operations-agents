#!/usr/bin/env python3
"""Shared helpers for suspended sessions (Phase 2–3)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SESSIONS_DIR = ROOT / "output/platform/sessions"
WEBHOOK_LOG = SESSIONS_DIR / "webhook-events.jsonl"


def load_session_files() -> list[dict[str, Any]]:
    if not SESSIONS_DIR.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(SESSIONS_DIR.glob("*.json")):
        if path.name == "webhook-events.jsonl":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_path"] = str(path)
            out.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return out


def load_suspended_sessions() -> list[dict[str, Any]]:
    return [s for s in load_session_files() if s.get("state") == "suspended"]


def save_session(session: dict[str, Any]) -> None:
    path = Path(session["_path"]) if session.get("_path") else SESSIONS_DIR / f"{session['session_id']}.json"
    payload = {k: v for k, v in session.items() if not k.startswith("_")}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    session["_path"] = str(path)


def check_session_status(session: dict[str, Any], token: str) -> dict[str, Any]:
    from check_approval_subtask import _find_subtask  # noqa: WPS433

    parent = session.get("parent_gid") or ""
    marker = session.get("marker") or "【承認】"
    sub = _find_subtask(parent, marker, token)
    if sub is None:
        status = "missing_gate"
    elif sub.get("completed"):
        status = "resumable"
    else:
        status = "wait"
    sub_gid = str(sub.get("gid")) if sub else session.get("approval_sub_gid")
    return {
        "session_id": session.get("session_id"),
        "status": status,
        "parent_gid": parent,
        "approval_sub_gid": sub_gid,
        "gate_kind": session.get("gate_kind"),
        "approval_url": session.get("approval_url"),
        "department": session.get("department"),
        "webhook_resumed_at": session.get("webhook_resumed_at"),
        "created_at": session.get("created_at"),
    }


def append_webhook_log(entry: dict[str, Any]) -> None:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    entry = {**entry, "logged_at": datetime.now(timezone.utc).isoformat()}
    with WEBHOOK_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_webhook_log(limit: int = 20) -> list[dict[str, Any]]:
    if not WEBHOOK_LOG.is_file():
        return []
    lines = WEBHOOK_LOG.read_text(encoding="utf-8").splitlines()
    out: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def handle_task_completed(task_gid: str) -> dict[str, Any] | None:
    """Mark matching suspended session when webhook reports task completion."""
    for session in load_suspended_sessions():
        if str(session.get("approval_sub_gid")) != str(task_gid):
            continue
        session["webhook_resumed_at"] = datetime.now(timezone.utc).isoformat()
        save_session(session)
        entry = {
            "event": "task.completed",
            "task_gid": task_gid,
            "session_id": session.get("session_id"),
            "gate_kind": session.get("gate_kind"),
        }
        append_webhook_log(entry)
        return entry
    entry = {"event": "task.completed", "task_gid": task_gid, "session_id": None}
    append_webhook_log(entry)
    return entry
