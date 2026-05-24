#!/usr/bin/env python3
"""List or check suspended workflow sessions (Phase 1).

Usage:
  python tools/check_workflow_suspend.py --list
  python tools/check_workflow_suspend.py --session <session_id>
  python tools/check_workflow_suspend.py --all --require-resumable
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
if str(ASANA_OPT) not in sys.path:
    sys.path.insert(0, str(ASANA_OPT))

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402

SESSIONS_DIR = ROOT / "output/platform/sessions"


def load_sessions() -> list[dict]:
    if not SESSIONS_DIR.is_dir():
        return []
    out: list[dict] = []
    for path in sorted(SESSIONS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_path"] = str(path)
            out.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return out


def check_one(session: dict, token: str) -> dict:
    from check_approval_subtask import _find_subtask  # noqa: WPS433

    parent = session.get("parent_gid") or ""
    marker = session.get("marker") or "【承認】"
    sub = _find_subtask(parent, marker, token)
    if sub is None:
        status = "missing_gate"
    elif sub.get("completed"):
        status = "resumable"
    else:
        status = "pending"
    return {
        "session_id": session.get("session_id"),
        "status": status,
        "parent_gid": parent,
        "approval_sub_gid": str(sub.get("gid")) if sub else session.get("approval_sub_gid"),
        "gate_kind": session.get("gate_kind"),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Check suspended workflow sessions")
    p.add_argument("--list", action="store_true")
    p.add_argument("--session", help="Session id prefix match")
    p.add_argument("--all", action="store_true", help="Check all suspended sessions")
    p.add_argument("--require-resumable", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    sessions = [s for s in load_sessions() if s.get("state") == "suspended"]
    if args.session:
        sessions = [s for s in sessions if (s.get("session_id") or "").startswith(args.session)]

    if args.list and not args.all and not args.session:
        for s in sessions:
            print(
                s.get("session_id"),
                s.get("gate_kind"),
                s.get("parent_gid"),
                s.get("approval_url") or "",
            )
        return 0

    load_env_from_dotfile()
    token = get_token()
    results = [check_one(s, token) for s in sessions]

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"{r['session_id']}\t{r['status']}\tparent={r['parent_gid']}")

    if args.require_resumable:
        pending = [r for r in results if r["status"] != "resumable"]
        if pending:
            return 1
        for r in results:
            if r["status"] == "resumable":
                print(f"RESUMABLE  session={r['session_id']}  gate={r['gate_kind']}  parent={r['parent_gid']}")
                print("  hint: python tools/pm_emit_resume_prompt.py --session", r["session_id"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
