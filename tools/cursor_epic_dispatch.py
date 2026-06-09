#!/usr/bin/env python3
"""Dispatch workflow-orchestrator / task-dispatcher via Cursor SDK (optional).

Usage:
  python tools/cursor_epic_dispatch.py --epic <PARENT> --mode planning --planning-child <GID> --dry-run
  python tools/cursor_epic_dispatch.py --epic <PARENT> --mode execution --gate-kind planning_approval -y

Requires CURSOR_API_KEY for -y. Without it: SKIP exit 0.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from cursor_sdk_kick import kick_prompt  # noqa: E402


def build_planning_prompt(epic_gid: str, planning_child: str) -> str:
    return (
        "あなたは planning-pm スキルです。\n"
        f"企画子タスク GID: {planning_child}\n"
        f"親エピック GID: {epic_gid}\n\n"
        "planning-delivery workflow に従い、Handoff 作成 → plan-reviewer → "
        "planning gate（デフォルト: 同一セッションで handoff_to_asana · opt-in 時は create_planning_approval_gate + チャット確認）まで進めてください。\n"
    )


def build_execution_prompt(epic_gid: str, gate_kind: str | None) -> str:
    gate = gate_kind or "planning_approval"
    return (
        "あなたは workflow-orchestrator スキルです（planning gate 承認後の RESUME）。\n"
        f"親エピック GID: {epic_gid}\n"
        f"gate_kind: {gate}\n\n"
        "この時点で execution 系子タスクはまだ Asana に存在しない。承認済み Handoff を"
        " Asana に sync して execution 子を作ってから dispatch すること。\n\n"
        "手順:\n"
        f"1. 親 {epic_gid} の epic 名に対応する Handoff を `output/planning/handoff/*.json` から特定する"
        "（`epic.title` が一致するもの。対の review は `output/planning/plan-review/<同名>.json`）。\n"
        "2. handoff_to_asana で execution 子を投入（冪等・重複親を作らない）:\n"
        "   python skills/platform/asana-buddy/optional/handoff_to_asana.py \\\n"
        "     --handoff output/planning/handoff/<theme>.json \\\n"
        "     --require-review-result output/planning/plan-review/<theme>.json \\\n"
        f"     --parent {epic_gid} -y --if-not-exists\n"
        f"3. python tools/task_dispatcher.py --parent {epic_gid} --kick -y\n"
        "4. PM 自身はワーカー役を代行しない（task-dispatcher → 各 PM intake へ委譲）。\n"
    )


def dispatch_cursor(prompt: str) -> int:
    return kick_prompt(
        prompt,
        cwd=ROOT,
        label="KICK",
        no_api_key_exit=2,
        no_sdk_exit=2,
        hint_manual=(
            "手動 planning-pm — Cursor で planning-pm として企画子 GID を dispatch"
        ),
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Cursor SDK epic dispatch (planning | execution)")
    p.add_argument("--epic", required=True, help="Parent epic GID")
    p.add_argument("--mode", choices=("planning", "execution"), required=True)
    p.add_argument("--planning-child", default=None)
    p.add_argument("--gate-kind", default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("-y", "--yes", action="store_true")
    args = p.parse_args()

    if args.mode == "planning":
        if not args.planning_child:
            print("error: --planning-child required for planning mode", file=sys.stderr)
            return 2
        prompt = build_planning_prompt(args.epic, args.planning_child)
    else:
        prompt = build_execution_prompt(args.epic, args.gate_kind)

    if args.dry_run or not args.yes:
        print(f"KICK  dry-run  mode={args.mode}  epic={args.epic}")
        print(prompt[:500])
        return 0
    return dispatch_cursor(prompt)


if __name__ == "__main__":
    sys.exit(main())
