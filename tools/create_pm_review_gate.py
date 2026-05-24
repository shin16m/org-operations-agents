#!/usr/bin/env python3
"""Create PM assign-review gate subtask after pm_assign_subtasks.

Usage:
  python tools/create_pm_review_gate.py --parent <PM子GID> --plan work/assign-plans/plan.json -y
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPTIONAL = ROOT / "skills/platform/asana-buddy/optional"
MARKER = "【レビュー】"
TITLE = f"{MARKER}サブ構成・担当割り当て"


def _summarize_plan(plan_path: Path) -> str:
    data = json.loads(plan_path.read_text(encoding="utf-8"))
    lines = ["## サブタスク一覧", ""]
    for i, item in enumerate(data.get("subtasks") or [], 1):
        assignee = item.get("assignee") or "（未設定）"
        lines.append(f"{i}. **{item.get('name') or item.get('title', '?')}** — 担当: `{assignee}`")
        if item.get("summary"):
            lines.append(f"   - {item['summary'].strip()[:120]}")
    lines.extend(
        [
            "",
            "## 依頼者向け",
            "",
            "PM が作成したサブタスク構成と担当割り当てを確認してください。",
            "問題なければ **このサブタスクを完了**（完了 = L3b worker dispatch 承認）。",
            "",
            "差し戻し: 本サブを未完了のまま、親にコメントで指摘 → PM が assign plan 再作成 → **新しいレビューサブ**を追加（既存サブは undo しない）。",
            "",
            "## CLI",
            "",
            "```powershell",
            f"python tools/check_pm_review_gate.py --parent <PM子GID>",
            "```",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Create PM assign-review gate subtask")
    p.add_argument("--parent", required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("-y", action="store_true")
    args = p.parse_args()

    notes_path = args.plan.with_suffix(".review-gate-notes.md")
    notes_path.write_text(_summarize_plan(args.plan), encoding="utf-8")

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
    print("review_gate_notes", notes_path)


if __name__ == "__main__":
    main()
