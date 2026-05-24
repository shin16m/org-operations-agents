#!/usr/bin/env python3
"""Emit resume dispatch snippets for approved suspended sessions (Phase 2).

Usage:
  python tools/pm_emit_resume_prompt.py --list
  python tools/pm_emit_resume_prompt.py --session <session_id_prefix>
  python tools/pm_emit_resume_prompt.py --all
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


def gate_status(session: dict, token: str) -> str:
    from check_approval_subtask import _find_subtask  # noqa: WPS433

    parent = session.get("parent_gid") or ""
    marker = session.get("marker") or "【承認】"
    sub = _find_subtask(parent, marker, token)
    if sub is None:
        return "missing_gate"
    return "resumable" if sub.get("completed") else "pending"


def emit_snippet(session: dict) -> str:
    gate = session.get("gate_kind") or "planning_approval"
    parent = session.get("parent_gid") or "?"
    sid = session.get("session_id") or "?"

    if gate == "pm_review_gate":
        dept = session.get("department") or "development"
        return f"""【ResumeDispatch】session={sid} gate={gate} parent={parent}

gate complete 済み。新規 Cursor セッションで worker dispatch:

python tools/pm_emit_worker_prompt.py --parent {parent} --department {dept}

PM review gate 後の L3b。親 {parent} の先頭 worker サブのみ実行すること。
"""

    return f"""【ResumeDispatch】session={sid} gate={gate} parent={parent}

planning gate complete 済み。新規 Cursor セッションで Asana 投入を続行:

python tools/check_workflow_suspend.py --all --require-resumable
# 続けて（Handoff / review JSON パスはセッション文脈に合わせる）
python skills/platform/asana-buddy/optional/handoff_to_asana.py \\
  --handoff output/planning/handoff/<theme>.json \\
  --require-review-result output/planning/plan-review/<theme>.json \\
  --parent {parent} -y --if-not-exists
"""


def main() -> int:
    p = argparse.ArgumentParser(description="Emit resume snippets for suspended sessions")
    p.add_argument("--list", action="store_true")
    p.add_argument("--session", help="Session id prefix")
    p.add_argument("--all", action="store_true", help="Emit all resumable sessions")
    args = p.parse_args()

    sessions = [s for s in load_sessions() if s.get("state") == "suspended"]
    if args.session:
        sessions = [s for s in sessions if (s.get("session_id") or "").startswith(args.session)]

    load_env_from_dotfile()
    token = get_token()

    rows: list[tuple[dict, str]] = []
    for s in sessions:
        status = gate_status(s, token)
        rows.append((s, status))
        if args.list:
            print(s.get("session_id"), status, s.get("gate_kind"), s.get("parent_gid"))

    if args.list:
        return 0

    resumable = [s for s, st in rows if st == "resumable"]
    if not resumable:
        pending = [s for s, st in rows if st == "pending"]
        if pending:
            s = pending[0]
            print(
                f"PENDING gate={s.get('gate_kind')} sub={s.get('approval_sub_gid')} "
                f"url={s.get('approval_url') or ''}",
                file=sys.stderr,
            )
            return 1
        print("no suspended sessions")
        return 0

    targets = resumable if args.all else resumable[:1]
    for s in targets:
        print(emit_snippet(s))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
