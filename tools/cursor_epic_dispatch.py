#!/usr/bin/env python3
"""Dispatch workflow-orchestrator / task-dispatcher via Cursor SDK (optional).

Usage:
  python tools/cursor_epic_dispatch.py --epic <PARENT> --mode planning --planning-child <GID> --dry-run
  python tools/cursor_epic_dispatch.py --epic <PARENT> --mode execution --gate-kind planning_approval -y

Requires CURSOR_API_KEY for -y. Without it: SKIP exit 0.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_planning_prompt(epic_gid: str, planning_child: str) -> str:
    return (
        "あなたは planning-pm スキルです。\n"
        f"企画子タスク GID: {planning_child}\n"
        f"親エピック GID: {epic_gid}\n\n"
        "planning-delivery workflow に従い、Handoff 作成 → plan-reviewer → "
        "planning gate（create_approval_subtask + --record-wait）まで進めてください。\n"
    )


def build_execution_prompt(epic_gid: str, gate_kind: str | None) -> str:
    gate = gate_kind or "planning_approval"
    return (
        "あなたは workflow-orchestrator スキルです（post-approval RESUME）。\n"
        f"親エピック GID: {epic_gid}\n"
        f"gate_kind: {gate}\n\n"
        "1. handoff_to_asana.py --require-review-result（未投入なら）\n"
        "2. task-dispatcher で未完了 execution 系子を各 PM に dispatch\n"
        "3. PM 自身はワーカー役を代行しない\n"
    )


def dispatch_cursor(prompt: str) -> int:
    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        print("SKIP  CURSOR_API_KEY unset — use poller --human snippet")
        return 0
    try:
        from cursor_sdk import Agent, AgentOptions, LocalAgentOptions  # type: ignore
    except ImportError:
        print("SKIP  cursor_sdk not installed")
        return 0
    print("KICK  cursor_sdk Agent.prompt starting…")
    result = Agent.prompt(
        prompt,
        AgentOptions(
            api_key=api_key,
            model="composer-2.5",
            local=LocalAgentOptions(cwd=str(ROOT)),
        ),
    )
    print(f"KICK  cursor_sdk status={result.status}")
    return 0


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
