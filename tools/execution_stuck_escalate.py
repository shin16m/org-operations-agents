#!/usr/bin/env python3
"""Detect Running epics stuck after planning complete; ESCALATE after N cycles."""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUCK_COUNTER_DIR = ROOT / "output/platform/execution-stuck"


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9))).isoformat(timespec="seconds")


def max_stuck_cycles() -> int:
    raw = os.environ.get("ORG_OPS_MAX_EXECUTION_STUCK_CYCLES", "5").strip()
    try:
        return max(1, int(raw))
    except ValueError:
        return 5


def _counter_path(epic_gid: str) -> Path:
    return STUCK_COUNTER_DIR / f"{epic_gid}.json"


def _read_counter(epic_gid: str) -> dict:
    p = _counter_path(epic_gid)
    if not p.is_file():
        return {"epic_gid": epic_gid, "cycle_count": 0, "history": []}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        data.setdefault("epic_gid", epic_gid)
        data.setdefault("cycle_count", 0)
        data.setdefault("history", [])
        return data
    except (OSError, json.JSONDecodeError):
        return {"epic_gid": epic_gid, "cycle_count": 0, "history": []}


def _write_counter(epic_gid: str, data: dict, max_cycles: int) -> None:
    STUCK_COUNTER_DIR.mkdir(parents=True, exist_ok=True)
    data["max_cycles"] = max_cycles
    data["updated_at"] = _now_iso()
    _counter_path(epic_gid).write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def reset_stuck_counter(epic_gid: str) -> None:
    p = _counter_path(epic_gid)
    if p.is_file():
        try:
            p.unlink()
        except OSError:
            pass


def detect_running_execution_stuck(
    epic_gid: str,
    item: dict,
    *,
    token: str,
) -> tuple[bool, str]:
    """Running + planning complete but execution chain not progressing."""
    from execution_kick_guard import _infer_planning_incomplete  # noqa: WPS433
    from org_os import asana_client  # noqa: WPS433
    from task_dispatcher import _epic_children  # noqa: WPS433

    task = asana_client.fetch_task(epic_gid, token)
    if asana_client.read_os_state(task) != "Running":
        return False, ""

    if _infer_planning_incomplete(epic_gid, token):
        return False, ""

    state = str(item.get("state") or "")
    reason = str(item.get("reason") or "")

    if state == "idle" and reason == "all_execution_complete":
        if not _epic_children(epic_gid, token):
            return True, "no_execution_children"
        return False, ""

    if state == "needs_pm_kick" and reason == "no_worker_subs":
        return True, "needs_pm_kick_no_workers"

    if state == "wait_worker_inflight" and reason == "worker_kick_inflight":
        from worker_kick_inflight import inflight_age_sec, stale_inflight_sec  # noqa: WPS433

        worker_gid = str(item.get("worker_sub_gid") or "")
        age = inflight_age_sec(worker_gid) if worker_gid else None
        if age is not None and age >= stale_inflight_sec():
            return True, f"worker_inflight_stale age_sec={age}"

    return False, ""


def tick_execution_stuck(
    epic_gid: str,
    stuck_reason: str,
    *,
    max_cycles: int | None = None,
    dry_run: bool = False,
    token: str | None = None,
) -> str | None:
    """Increment stuck counter. Returns WARN, ESCALATE, or None (not stuck)."""
    from asana_program_common import console_safe  # noqa: WPS433

    limit = max_cycles if max_cycles is not None else max_stuck_cycles()
    counter = _read_counter(epic_gid)
    counter["cycle_count"] = int(counter.get("cycle_count", 0)) + 1
    history = list(counter.get("history") or [])
    history.append({"reason": stuck_reason, "at": _now_iso()})
    counter["history"] = history[-10:]
    _write_counter(epic_gid, counter, limit)

    count = counter["cycle_count"]
    if count >= limit:
        print(
            console_safe(
                f"ESCALATE parent={epic_gid}  count={count}/{limit}  "
                f"reason={stuck_reason}  phase=execution_stuck"
            ),
            file=sys.stderr,
        )
        if not dry_run and token:
            _post_escalation_comment(epic_gid, counter, limit, stuck_reason, token)
        return "ESCALATE"

    print(
        console_safe(
            f"WARN  execution_stuck  parent={epic_gid}  count={count}/{limit}  "
            f"reason={stuck_reason}"
        ),
        file=sys.stderr,
    )
    return "WARN"


def _post_escalation_comment(
    epic_gid: str,
    counter: dict,
    max_cycles: int,
    stuck_reason: str,
    token: str,
) -> None:
    import os as _os

    import requests  # noqa: WPS433

    from asana_program_common import create_task_story_html, html_user_mention_tag  # noqa: WPS433

    esc = _os.getenv("ASANA_DEFAULT_HUMAN_APPROVER_GID", "").strip() or None
    mention_html = html_user_mention_tag(esc) if esc else ""
    html_body = (
        "<body>"
        "<strong>execution チェーン stuck 上限到達</strong>"
        f"{(' ' + mention_html) if mention_html else ''} "
        f"企画完了後 OS=Running のまま <strong>{counter['cycle_count']}/{max_cycles}</strong> "
        f"サイクル進展がありません（reason=<code>{stuck_reason}</code>）。"
        "手動で cursor_epic_dispatch / task_dispatcher を確認してください。"
        f" ログ: output/platform/execution-stuck/{epic_gid}.json"
        "</body>"
    )
    try:
        create_task_story_html(epic_gid, html_body, token)
    except requests.HTTPError as exc:
        print(f"warn  execution escalation comment failed epic={epic_gid}: {exc}", file=sys.stderr)


def check_and_emit_stuck(
    epic_gid: str,
    item: dict,
    *,
    token: str,
    dry_run: bool = False,
    max_cycles: int | None = None,
) -> str | None:
    """Detect stuck; tick counter or reset when clear."""
    stuck, reason = detect_running_execution_stuck(epic_gid, item, token=token)
    if not stuck:
        if not dry_run:
            reset_stuck_counter(epic_gid)
        return None
    return tick_execution_stuck(
        epic_gid,
        reason,
        max_cycles=max_cycles,
        dry_run=dry_run,
        token=token,
    )
