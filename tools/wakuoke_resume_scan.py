#!/usr/bin/env python3
"""Scan Asana project for Ready epics and reconcile with approval-helper logs.

For each watch epic (Agent Type=AI · Task Type=Epic) with `OS State=Ready`:
  - if no approval-helper log exists: print READY (fresh dispatch lane)
  - if log exists with approval_result=OK: print RESUME (next: execution dispatch)
      and mark the log `consumed: true`
  - if log exists with approval_result=NG / null:
      increment NG counter and either print RESUME(ng) or ESCALATE
      depending on `--max-ng`; on escalation post a comment to the parent epic
      (skipped when `--dry-run`).

Outputs are line-oriented and meant to be consumed by org-ops orchestration.

Usage:
  python tools/wakuoke_resume_scan.py --project <PROJECT_GID> --dry-run
  python tools/wakuoke_resume_scan.py --project <PROJECT_GID> --max-ng 3
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
ORG_OS_SRC = ROOT / "products/org-os/src"
for p in (ASANA_OPT, ORG_OS_SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import requests  # noqa: E402

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import console_safe, create_task_story_html, html_user_mention_tag  # noqa: E402
from org_os import queue as org_os_queue  # noqa: E402

HELPER_LOG_DIR = ROOT / "output/platform/approval-helper"
NG_COUNTER_DIR = HELPER_LOG_DIR / "ng-counters"


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9))).isoformat(timespec="seconds")


def _find_helper_logs(parent_gid: str) -> list[Path]:
    if not HELPER_LOG_DIR.is_dir():
        return []
    return sorted(
        HELPER_LOG_DIR.glob(f"{parent_gid}-*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def _load_log(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"warn  helper log read fail {path}: {exc}", file=sys.stderr)
        return {}


def _mark_consumed(path: Path, payload: dict) -> None:
    payload["consumed"] = True
    payload["consumed_at"] = _now_iso()
    try:
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"warn  helper log write fail {path}: {exc}", file=sys.stderr)


def _ng_counter_path(parent_gid: str) -> Path:
    return NG_COUNTER_DIR / f"{parent_gid}.json"


def _read_ng_counter(parent_gid: str) -> dict:
    p = _ng_counter_path(parent_gid)
    if not p.is_file():
        return {"parent_gid": parent_gid, "ng_count": 0, "history": []}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        data.setdefault("parent_gid", parent_gid)
        data.setdefault("ng_count", 0)
        data.setdefault("history", [])
        return data
    except (OSError, json.JSONDecodeError):
        return {"parent_gid": parent_gid, "ng_count": 0, "history": []}


def _write_ng_counter(parent_gid: str, data: dict, max_ng: int) -> None:
    NG_COUNTER_DIR.mkdir(parents=True, exist_ok=True)
    data["max_ng"] = max_ng
    data["updated_at"] = _now_iso()
    p = _ng_counter_path(parent_gid)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _post_escalation_comment(
    parent_gid: str,
    counter: dict,
    max_ng: int,
    escalation_user: str | None,
    token: str,
) -> None:
    mention_html = html_user_mention_tag(escalation_user) if escalation_user else ""
    html_body = (
        "<body>"
        "<strong>NG ループ上限到達</strong>"
        f"{(' ' + mention_html) if mention_html else ''} "
        f"承認サブで <code>Approval Result=NG</code>（または未設定で完了）が "
        f"<strong>{counter['ng_count']}/{max_ng}</strong> 回連続しました。"
        "和久桶セッションでの自動再開は停止します。本エピックは依頼者の判断で next action を決定してください。 "
        f"history: 直近 {len(counter.get('history') or [])} 件をログに記録"
        f"（output/platform/approval-helper/ng-counters/{parent_gid}.json）。"
        "</body>"
    )
    try:
        create_task_story_html(parent_gid, html_body, token)
    except requests.HTTPError as exc:
        print(f"warn  escalation comment failed parent={parent_gid}: {exc}", file=sys.stderr)


def _resolve_project(arg_project: str | None) -> str | None:
    if arg_project:
        return arg_project
    for key in ("ASANA_PROJECT_ID", "ASANA_PROJECT_GID", "ASANA_PROJECT"):
        val = os.getenv(key, "").strip()
        if val:
            return val
    return None


def main() -> int:
    p = argparse.ArgumentParser(
        description="Scan Asana for Ready epics and reconcile with approval-helper logs."
    )
    p.add_argument("--project", default=None)
    p.add_argument("--max-ng", type=int, default=3)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--escalation-user", default=None)
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()
    project = _resolve_project(args.project)
    if not project:
        print("error: --project not provided and ASANA_PROJECT_ID unset", file=sys.stderr)
        return 2

    escalation_user = (
        args.escalation_user
        or os.getenv("ASANA_DEFAULT_HUMAN_APPROVER_GID", "").strip()
        or None
    )

    print(console_safe(f"SCAN  project={project}  max_ng={args.max_ng}  dry_run={args.dry_run}"))

    try:
        ready_rows = org_os_queue.ready_queue(project, token=token)
    except requests.HTTPError as exc:
        print(f"error: failed to list ready queue: {exc}", file=sys.stderr)
        return 3

    ready_count = len(ready_rows)
    for row in ready_rows:
        parent_gid = str(row.get("epic_gid") or "")

        logs = _find_helper_logs(parent_gid)
        active_log: tuple[Path, dict] | None = None
        for log_path in logs:
            payload = _load_log(log_path)
            if payload and not payload.get("consumed", False):
                active_log = (log_path, payload)
                break

        if active_log is None:
            print(console_safe(f"READY  parent={parent_gid}  kind=fresh"))
            continue

        log_path, payload = active_log
        result = payload.get("approval_result")
        if result == "OK":
            print(console_safe(f"RESUME parent={parent_gid}  result=OK  next=execution_dispatch"))
            _mark_consumed(log_path, payload)
            continue

        counter = _read_ng_counter(parent_gid)
        counter["ng_count"] = int(counter.get("ng_count", 0)) + 1
        history = list(counter.get("history") or [])
        history.append(
            {
                "sub_gid": payload.get("approval_sub_gid"),
                "completed_at": payload.get("completed_at"),
                "result": result,
                "excerpt": payload.get("approval_comments_excerpt", ""),
            }
        )
        counter["history"] = history[-10:]
        _write_ng_counter(parent_gid, counter, args.max_ng)
        _mark_consumed(log_path, payload)

        if counter["ng_count"] >= args.max_ng:
            print(console_safe(
                f"ESCALATE parent={parent_gid}  count={counter['ng_count']}/{args.max_ng}  result={result or 'unset'}"
            ))
            if not args.dry_run:
                _post_escalation_comment(parent_gid, counter, args.max_ng, escalation_user, token)
        else:
            print(console_safe(
                f"RESUME parent={parent_gid}  result={result or 'unset'}  count={counter['ng_count']}/{args.max_ng}"
            ))

    print(console_safe(f"DONE  ready_total={ready_count}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
