#!/usr/bin/env python3
"""Create epic retrospective intake approval gate subtask.

Usage:
  python tools/create_retrospective_intake_gate.py --parent <EPIC_GID> --retro <epic-retro.json> -y
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPTIONAL = ROOT / "skills/platform/asana-buddy/optional"
MARKER = "【承認】"
TITLE = f"{MARKER}レトロ改善候補 → intake 起票"


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
    p = argparse.ArgumentParser(description="Create retrospective intake approval gate")
    p.add_argument("--parent", required=True)
    p.add_argument("--retro", type=Path, required=True)
    p.add_argument("-y", action="store_true")
    args = p.parse_args()

    notes_path = args.retro.with_suffix(".intake-gate-notes.md")
    notes_path.write_text(_notes_from_retro(args.retro), encoding="utf-8")

    cmd = [
        sys.executable,
        str(OPTIONAL / "create_approval_subtask.py"),
        "--parent",
        args.parent,
        "--title",
        TITLE,
        "--notes-file",
        str(notes_path),
    ]
    if args.y:
        cmd.append("-y")
    subprocess.check_call(cmd, cwd=str(ROOT))
    print("intake_gate_notes", notes_path)


if __name__ == "__main__":
    main()
