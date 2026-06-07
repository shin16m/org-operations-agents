#!/usr/bin/env python3
"""Epic complete hook — retrospective intake gate WARN (Phase 2).

Runs before org-os complete / complete_task on epics. Posts Asana WARN comments when
retro intake gate is missing or pending. Blocking is opt-in via ORG_OPS_RETRO_COMPLETE_BLOCK.

Usage:
  python tools/epic_retrospective_complete_hook.py --epic <EPIC_GID>
  python tools/epic_retrospective_complete_hook.py --epic <EPIC_GID> --dry-run
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
OPTIONAL = ROOT / "skills/platform/asana-buddy/optional"
PY = ROOT / ".venv/Scripts/python.exe"
if not PY.is_file():
    PY = Path(sys.executable)

for p in (str(TOOLS), str(OPTIONAL)):
    if p not in sys.path:
        sys.path.insert(0, p)

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import console_safe, create_task_story  # noqa: E402
from retrospective_intake_gate_util import (  # noqa: E402
    find_retro_intake_gate_sub,
    human_retro_intake_gate_requested,
)

WARN_MARKER = "org-ops WARN retro-intake-gate"


@dataclass(frozen=True)
class RetroGateEvaluation:
    kind: str  # ok | missing | pending
    message: str
    subtask_gid: str | None = None
    check_exit: int = 0


def _block_on_failure() -> bool:
    return os.environ.get("ORG_OPS_RETRO_COMPLETE_BLOCK", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def run_check_retrospective_intake_gate(epic_gid: str) -> int:
    r = subprocess.run(
        [str(PY), str(TOOLS / "check_retrospective_intake_gate.py"), "--parent", epic_gid],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return int(r.returncode)


def evaluate_retro_gate(epic_gid: str, token: str) -> RetroGateEvaluation:
    sub = find_retro_intake_gate_sub(epic_gid, token)
    check_exit = run_check_retrospective_intake_gate(epic_gid)

    if sub is None:
        if human_retro_intake_gate_requested(parent_gid=epic_gid, token=token):
            msg = (
                "opt-in retro intake gate が要求されていますが、【承認】レトロ改善候補 サブが未作成です。"
                " create_retrospective_intake_gate.py を実行してください。"
            )
        else:
            msg = (
                "retro intake gate 未作成（デフォルト opt-out · 任意で "
                "create_retrospective_intake_gate.py → check_retrospective_intake_gate.py）。"
            )
        return RetroGateEvaluation(
            kind="missing",
            message=msg,
            check_exit=check_exit,
        )

    if not sub.get("completed"):
        return RetroGateEvaluation(
            kind="pending",
            message=(
                "retro intake gate が未承認です。依頼者が Asana UI で "
                f"【承認】サブ ({sub.get('gid')}) を complete してください。"
            ),
            subtask_gid=str(sub.get("gid") or "") or None,
            check_exit=check_exit,
        )

    return RetroGateEvaluation(kind="ok", message="retro intake gate OK", check_exit=check_exit)


def build_warn_comment(evaluation: RetroGateEvaluation) -> str | None:
    if evaluation.kind == "ok":
        return None
    return f"{WARN_MARKER}\n\n{evaluation.message}"


def post_warn_comment(epic_gid: str, text: str, token: str, *, dry_run: bool) -> None:
    if dry_run:
        print(f"DRY-RUN  warn_comment  epic={epic_gid}\n{text}")
        return
    create_task_story(epic_gid, text, token)
    print(console_safe(f"WARN  retro_intake_gate  epic={epic_gid}  comment posted"))


def run_epic_retrospective_gate_hook(
    epic_gid: str,
    *,
    token: str | None = None,
    dry_run: bool = False,
) -> int:
    """Evaluate retro gate; WARN on missing/pending. Return exit code for callers."""
    if token is None:
        load_env_from_dotfile()
        token = get_token()

    evaluation = evaluate_retro_gate(epic_gid, token)
    warn_text = build_warn_comment(evaluation)
    if warn_text:
        post_warn_comment(epic_gid, warn_text, token, dry_run=dry_run)
        print(console_safe(f"WARN  retro_intake_gate  kind={evaluation.kind}  epic={epic_gid}"))

    if evaluation.kind == "ok":
        return 0

    if _block_on_failure() or evaluation.check_exit != 0:
        if _block_on_failure():
            print(
                console_safe(
                    "ERROR  retro_intake_gate  blocked  "
                    "(ORG_OPS_RETRO_COMPLETE_BLOCK=1)"
                ),
                file=sys.stderr,
            )
            return 1
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Epic complete retro intake gate WARN hook")
    p.add_argument("--epic", required=True, help="Epic parent GID")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    return run_epic_retrospective_gate_hook(args.epic, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
