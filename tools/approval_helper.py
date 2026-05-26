#!/usr/bin/env python3
"""Watch an approval subtask and restore parent epic CF on completion.

Polls the approval subtask `completed` flag and—on completion—reads the human
selected `Approval Result` enum (OK/NG/未設定) and resets the parent epic to
`OS State=Ready` + `Approval Required=No`. Designed to be invoked on demand
by org-ops orchestration and exits when the approval is settled.

Usage:
  python tools/approval_helper.py \\
      --parent <EPIC_GID> --approval-sub <SUB_GID> \\
      --gate-kind planning_approval --once
  python tools/approval_helper.py \\
      --parent <EPIC_GID> --approval-sub <SUB_GID> \\
      --gate-kind pm_review_gate --interval 30 --timeout 604800

Exit codes:
  0   approval detected, parent CF restored, log JSON written
  1   --once and approval is still pending (no log)
  2   approval subtask not found under parent
  124 timeout reached without approval
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
ORG_OS_SRC = ROOT / "products/org-os/src"
for p in (ASANA_OPT, ORG_OS_SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    console_safe,
    list_subtasks,
    read_approval_result,
)
from org_os import syscall  # noqa: E402

HELPER_VERSION = "1.0"
DEFAULT_LOG_DIR = ROOT / "output/platform/approval-helper"


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9))).isoformat(timespec="seconds")


def _find_subtask(parent_gid: str, sub_gid: str, token: str) -> dict | None:
    for s in list_subtasks(parent_gid, token):
        if str(s.get("gid")) == sub_gid:
            return s
    return None


def _save_log(log_dir: Path, parent_gid: str, sub_gid: str, payload: dict) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"{parent_gid}-{sub_gid}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _restore_parent(parent_gid: str, token: str, ref: str | None = None) -> bool:
    try:
        syscall.resume(parent_gid, ref=ref)
        return True
    except Exception as exc:  # noqa: BLE001
        print(
            f"警告: 親 resume 失敗 parent={parent_gid}: {exc}",
            file=sys.stderr,
        )
        return False


def main() -> int:
    p = argparse.ArgumentParser(
        description="Watch approval subtask completion and restore parent epic CF."
    )
    p.add_argument("--parent", required=True, help="Parent epic GID")
    p.add_argument("--approval-sub", required=True, help="Approval subtask GID")
    p.add_argument(
        "--gate-kind",
        required=True,
        choices=("planning_approval", "pm_review_gate"),
        help="Gate kind (recorded in log only).",
    )
    p.add_argument("--interval", type=int, default=30, help="Poll interval in seconds (default 30)")
    p.add_argument(
        "--timeout",
        type=int,
        default=604800,
        help="Total timeout in seconds (default 7 days)",
    )
    p.add_argument(
        "--once",
        action="store_true",
        help="Check once and exit (1 if pending, 0 if approved, 2 if missing).",
    )
    p.add_argument(
        "--log-dir",
        default=str(DEFAULT_LOG_DIR),
        help="Directory to write helper log JSON (default output/platform/approval-helper).",
    )
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()
    started_at = _now_iso()
    deadline = time.monotonic() + args.timeout

    while True:
        sub = _find_subtask(args.parent, args.approval_sub, token)
        if sub is None:
            print(
                console_safe(
                    f"MISSING approval subtask {args.approval_sub} under parent {args.parent}"
                ),
                file=sys.stderr,
            )
            return 2

        if bool(sub.get("completed")):
            result_name = read_approval_result(args.approval_sub, token)
            ok = _restore_parent(args.parent, token, ref=args.approval_sub)
            payload = {
                "helper_version": HELPER_VERSION,
                "parent_gid": args.parent,
                "approval_sub_gid": args.approval_sub,
                "gate_kind": args.gate_kind,
                "started_at": started_at,
                "completed_at": _now_iso(),
                "approval_result": result_name,
                "approval_comments_excerpt": (sub.get("notes") or "")[:200],
                "parent_state_after": {
                    "os_state": "Ready" if ok else "unchanged",
                    "approval_required": "No" if ok else "unchanged",
                    "suspend_reason": None if ok else "unchanged",
                },
                "consumed": False,
            }
            log_path = _save_log(Path(args.log_dir), args.parent, args.approval_sub, payload)
            print(
                console_safe(
                    f"APPROVED sub={args.approval_sub} result={result_name or 'unset'} log={log_path}"
                )
            )
            return 0

        if args.once:
            print(
                console_safe(
                    f"PENDING sub={args.approval_sub} (no log written)"
                )
            )
            return 1

        if time.monotonic() > deadline:
            print(
                console_safe(f"TIMEOUT sub={args.approval_sub} after {args.timeout}s"),
                file=sys.stderr,
            )
            return 124

        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
