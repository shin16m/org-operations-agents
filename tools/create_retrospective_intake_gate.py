#!/usr/bin/env python3
"""Create epic retrospective intake approval gate (default-on · Phase 2).

Default: create 【承認】 gate. Opt-out with:
  --skip-gate
  env ORG_OPS_RETRO_INTAKE_GATE_OPT_OUT=1

Legacy opt-in triggers still honored when not opted out:
  --require-human-approval
  retro JSON \"human_retro_intake_gate\": true
  env ORG_OPS_RETRO_INTAKE_GATE=1
  epic notes: human_retro_intake_gate: yes

Usage:
  python tools/create_retrospective_intake_gate.py --parent <EPIC_GID> --retro <epic-retro.json> -y
  python tools/create_retrospective_intake_gate.py --parent <GID> --retro retro.json --require-human-approval -y
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
from retrospective_intake_gate_util import (  # noqa: E402
    GATE_TITLE,
    human_retro_intake_gate_requested,
)


def _notes_from_retro(retro_path: Path) -> str:
    data = json.loads(retro_path.read_text(encoding="utf-8"))
    lines = ["## intake 候補一覧", ""]
    cands = data.get("intake_candidates") or []
    if not cands:
        lines.append("（候補なし — 空でも承認 complete でエピック完了フロー続行可）")
    else:
        for i, c in enumerate(cands, 1):
            lines.append(f"{i}. **{c.get('summary', '?')}**")
            lines.append(f"   - 出典: task `{c.get('source_task_gid')}` · agent `{c.get('source_agent')}`")
    lines.extend(
        [
            "",
            "## 依頼者向け",
            "",
            "採用する候補を確認し、必要なら **本サブのコメント** に追記・修正指示を書いてください。",
            "問題なければ **このサブタスクを完了**（完了 = 記載候補の intake 起票を承認）。",
            "",
            "却下する候補はコメントで `- 却下: <番号>` と明記。未記載候補は起票しません。",
            "",
            "## CLI（承認後 · エージェント）",
            "",
            "```powershell",
            f"python tools/check_retrospective_intake_gate.py --parent {data.get('parent_gid', '<EPIC>')}",
            f"python tools/create_retrospective_intake_tasks.py --parent {data.get('parent_gid', '<EPIC>')} --retro {retro_path.as_posix()} -y",
            "```",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Create retrospective intake approval gate (opt-in)")
    p.add_argument("--parent", required=True)
    p.add_argument("--retro", type=Path, required=True)
    p.add_argument(
        "--require-human-approval",
        action="store_true",
        help="Force create human 【承認】 gate (legacy alias)",
    )
    p.add_argument(
        "--skip-gate",
        action="store_true",
        help="Opt-out: do not create gate sub",
    )
    p.add_argument("-y", action="store_true")
    args = p.parse_args()

    notes_path = args.retro.with_suffix(".intake-gate-notes.md")
    notes_path.write_text(_notes_from_retro(args.retro), encoding="utf-8")

    token = None
    if args.y:
        load_env_from_dotfile()
        token = get_token()

    if not human_retro_intake_gate_requested(
        args.retro,
        args.parent,
        token,
        cli_flag=args.require_human_approval,
        cli_skip=args.skip_gate,
    ):
        print(
            console_safe(
                "SKIP  retro_intake_gate  reason=opt_out  "
                "(default is ON; use --skip-gate or ORG_OPS_RETRO_INTAKE_GATE_OPT_OUT=1 to skip)"
            )
        )
        return 0

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
    print("intake_gate_notes", notes_path)


if __name__ == "__main__":
    main()
