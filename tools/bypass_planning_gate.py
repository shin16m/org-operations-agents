#!/usr/bin/env python3
"""Bypass planning gate when operator authorizes skip (writes approval log + resume)."""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
ORG_OS_SRC = ROOT / "products/org-os/src"
for p in (ASANA_OPT, ORG_OS_SRC, ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from org_os import syscall  # noqa: E402

HELPER_VERSION = "1.0"
LOG_DIR = ROOT / "output/platform/approval-helper"


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9))).isoformat(timespec="seconds")


def bypass_planning_gate(epic_gid: str, sub_gid: str) -> Path:
    load_env_from_dotfile()
    try:
        syscall.resume(epic_gid, ref=sub_gid)
        print(f"RESUME  epic={epic_gid}")
    except Exception as exc:  # noqa: BLE001
        print(f"WARN  resume skipped epic={epic_gid}: {exc}", file=sys.stderr)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / f"{epic_gid}-{sub_gid}.json"
    payload = {
        "helper_version": HELPER_VERSION,
        "parent_gid": epic_gid,
        "approval_sub_gid": sub_gid,
        "gate_kind": "planning_approval",
        "started_at": _now_iso(),
        "completed_at": _now_iso(),
        "approval_result": "OK",
        "approval_comments_excerpt": "operator bypass (chat authorized)",
        "parent_state_after": {
            "os_state": "Ready",
            "approval_required": "No",
            "suspend_reason": None,
        },
        "consumed": False,
        "bypass": True,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"LOG  path={path}")
    return path


def main() -> int:
    p = argparse.ArgumentParser(description="Bypass planning gate with OK log + resume")
    p.add_argument("--epic", required=True)
    p.add_argument("--approval-sub", required=True)
    args = p.parse_args()
    bypass_planning_gate(args.epic, args.approval_sub)
    return 0


if __name__ == "__main__":
    sys.exit(main())
