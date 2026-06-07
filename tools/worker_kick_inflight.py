#!/usr/bin/env python3
"""In-flight marker for L3b worker kicks (kick start → agent comment)."""
from __future__ import annotations

import datetime as _dt
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INFLIGHT_DIR = ROOT / "output/platform/worker-inflight"


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9))).isoformat(timespec="seconds")


def inflight_ttl_sec() -> int:
    raw = os.environ.get("ORG_OPS_WORKER_INFLIGHT_TTL_SEC", "7200").strip()
    try:
        return max(60, int(raw))
    except ValueError:
        return 7200


def stale_inflight_sec() -> int:
    """Age after which execution_stuck_escalate may treat inflight as stuck."""
    raw = os.environ.get("ORG_OPS_WORKER_INFLIGHT_STUCK_SEC", "600").strip()
    try:
        return max(60, int(raw))
    except ValueError:
        return 600


def _path(worker_gid: str) -> Path:
    return INFLIGHT_DIR / f"{worker_gid}.json"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _started_at_epoch(data: dict[str, Any]) -> float | None:
    raw = (data.get("started_at") or "").strip()
    if not raw:
        return None
    try:
        dt = _dt.datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=_dt.timezone(_dt.timedelta(hours=9)))
        return dt.timestamp()
    except ValueError:
        return None


def inflight_age_sec(worker_gid: str) -> int | None:
    path = _path(worker_gid)
    if not path.is_file():
        return None
    try:
        data = _read(path)
    except (OSError, json.JSONDecodeError):
        return None
    started = _started_at_epoch(data)
    if started is None:
        return None
    return max(0, int(_dt.datetime.now(_dt.timezone.utc).timestamp() - started))


def clear_stale(worker_gid: str) -> bool:
    """Remove inflight marker when TTL exceeded. Returns True if cleared."""
    path = _path(worker_gid)
    if not path.is_file():
        return False
    try:
        data = _read(path)
    except (OSError, json.JSONDecodeError):
        path.unlink(missing_ok=True)
        return True
    started = _started_at_epoch(data)
    if started is None:
        return False
    age = _dt.datetime.now(_dt.timezone.utc).timestamp() - started
    if age > inflight_ttl_sec():
        path.unlink(missing_ok=True)
        return True
    return False


def is_worker_kick_inflight(worker_gid: str) -> bool:
    clear_stale(worker_gid)
    return _path(worker_gid).is_file()


def claim_worker_kick(
    worker_gid: str,
    *,
    epic_gid: str,
    pm_child_gid: str,
    tool: str,
) -> tuple[bool, str]:
    """Return (claimed, reason). False when another kick is in-flight."""
    clear_stale(worker_gid)
    path = _path(worker_gid)
    if path.is_file():
        try:
            data = _read(path)
        except (OSError, json.JSONDecodeError):
            data = {}
        return False, f"worker_inflight={worker_gid} tool={data.get('tool') or '?'}"

    INFLIGHT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "worker_gid": worker_gid,
        "epic_gid": epic_gid,
        "pm_child_gid": pm_child_gid,
        "tool": tool,
        "started_at": _now_iso(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True, "ok"


def release_worker_kick(worker_gid: str) -> None:
    _path(worker_gid).unlink(missing_ok=True)
