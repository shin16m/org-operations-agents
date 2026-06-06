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


def approval_sub_resume_status(session: dict[str, Any], token: str) -> str:
    """Return resumable | wait | missing_gate using session.approval_sub_gid."""
    from asana_program_common import fetch_task  # noqa: WPS433

    sub_gid = session.get("approval_sub_gid")
    if not sub_gid:
        return "missing_gate"
    try:
        task = fetch_task(str(sub_gid), token)
    except Exception:  # noqa: BLE001
        return "missing_gate"
    if task.get("completed"):
        return "resumable"
    return "wait"


def check_session_status(session: dict[str, Any], token: str) -> dict[str, Any]:
    parent = session.get("parent_gid") or ""
    sub_gid = session.get("approval_sub_gid")
    status = approval_sub_resume_status(session, token)
    if status == "resumable":
        gate_status = "resumable"
    elif status == "wait":
        gate_status = "wait"
    else:
        gate_status = "missing_gate"
    return {
        "session_id": session.get("session_id"),
        "status": gate_status,
        "parent_gid": parent,
        "approval_sub_gid": str(sub_gid) if sub_gid else None,
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


ARCHIVE_DIR = SESSIONS_DIR / "archive"


def archive_resumable_sessions(token: str, *, dry_run: bool = False) -> int:
    """Move gate-complete suspended sessions to archive/ (reduces poller WAIT noise)."""
    moved = 0
    for session in load_suspended_sessions():
        status = check_session_status(session, token)
        if status.get("status") != "resumable":
            continue
        sid = session.get("session_id") or "?"
        path = Path(session["_path"]) if session.get("_path") else None
        if dry_run:
            print(f"ARCHIVE  dry-run  session={sid}  parent={session.get('parent_gid')}")
            moved += 1
            continue
        if path is None or not path.is_file():
            continue
        session["state"] = "archived"
        session["archived_at"] = datetime.now(timezone.utc).isoformat()
        payload = {k: v for k, v in session.items() if not k.startswith("_")}
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        dest = ARCHIVE_DIR / path.name
        dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        path.unlink(missing_ok=True)
        print(f"ARCHIVE  session={sid}  parent={session.get('parent_gid')}  path={dest}")
        moved += 1
    return moved


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
