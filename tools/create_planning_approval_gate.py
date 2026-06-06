#!/usr/bin/env python3
"""Create planning gate (handoff_approved) subtask — opt-in human approval.

By default (opt-out) no Asana gate sub is created. Enable with:
  --require-human-approval
  Handoff meta \"human_planning_approval\": true
  env ORG_OPS_PLANNING_APPROVAL_GATE=1
  epic notes: human_planning_approval: yes

Usage:
  python tools/create_planning_approval_gate.py --parent <親エピックGID> --handoff output/planning/handoff/foo.json -y
  python tools/create_planning_approval_gate.py --parent <GID> --handoff foo.json --require-human-approval -y
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
OPTIONAL = ROOT / "skills/platform/asana-buddy/optional"
for p in (str(TOOLS), str(OPTIONAL)):
    if p not in sys.path:
        sys.path.insert(0, p)

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import console_safe  # noqa: E402
from planning_approval_gate_util import (  # noqa: E402
    GATE_TITLE,
    human_planning_approval_requested,
)


def _summarize_handoff(handoff_path: Path) -> str:
    data = json.loads(handoff_path.read_text(encoding="utf-8"))
    epic = data.get("epic") or {}
    lines = [
        "## Handoff 要約",
        "",
        f"**エピック:** {epic.get('title', '?')}",
        "",
        "## 子タスク一覧",
        "",
    ]
    for i, item in enumerate(data.get("subtasks") or [], 1):
        dept = item.get("department") or "?"
        lines.append(f"{i}. **{item.get('title') or item.get('name', '?')}** — `{dept}`")
        if item.get("summary"):
            lines.append(f"   - {str(item['summary']).strip()[:120]}")
    lines.extend(
        [
            "",
            "## 依頼者向け",
            "",
            "Handoff 内容を確認してください。",
            "問題なければ **Approval Result=OK を選択してからこのサブタスクを完了**（完了 = execution 系子の Asana 投入承認）。",
            "",
            "差し戻し: **Approval Result=NG** を選択し、コメントで指摘してから完了してください。",
            "",
            "## CLI（承認後 · エージェント）",
            "",
            "```powershell",
            "python tools/check_planning_approval_gate.py --parent <親エピックGID>",
            "python skills/platform/asana-buddy/optional/handoff_to_asana.py --handoff "
            f"{handoff_path.as_posix()} --require-review-result -y --if-not-exists",
            "```",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Create planning approval gate subtask (opt-in)")
    p.add_argument("--parent", required=True, help="Parent epic GID")
    p.add_argument("--handoff", type=Path, required=True, help="Handoff JSON path")
    p.add_argument(
        "--require-human-approval",
        action="store_true",
        help="Force create human 【承認】 gate (evaluation / audit)",
    )
    p.add_argument("-y", action="store_true")
    args = p.parse_args()

    notes_path = args.handoff.with_suffix(".approval-gate-notes.md")
    notes_path.write_text(_summarize_handoff(args.handoff), encoding="utf-8")
    print(f"approval_gate_notes  {notes_path}")

    token = None
    if args.y:
        load_env_from_dotfile()
        token = get_token()

    if not human_planning_approval_requested(
        args.handoff,
        args.parent,
        token,
        cli_flag=args.require_human_approval,
    ):
        print(
            console_safe(
                "SKIP  planning_approval_gate  reason=opt_out_default  "
                "(use --require-human-approval | handoff human_planning_approval | "
                "ORG_OPS_PLANNING_APPROVAL_GATE=1 | epic notes human_planning_approval: yes)"
            )
        )
        return

    cmd = [
        sys.executable,
        str(OPTIONAL / "create_approval_subtask.py"),
        "--parent",
        args.parent,
        "--title",
        GATE_TITLE,
        "--notes-file",
        str(notes_path),
    ]
    if args.y:
        cmd.append("-y")
    subprocess.check_call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    main()
