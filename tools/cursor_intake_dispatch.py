#!/usr/bin/env python3
"""PoC: dispatch workflow-orchestrator intake-asana via Cursor SDK (optional).

Usage:
  python tools/cursor_intake_dispatch.py --task <GID> --dry-run
  python tools/cursor_intake_dispatch.py --task <GID> -y

Requires CURSOR_API_KEY for -y execution. Without it, prints SKIP and exit 0.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTAKE_DIR = ROOT / "output/platform/intake"


def build_prompt(task_gid: str, snapshot_path: Path) -> str:
    return (
        "あなたは workflow-orchestrator スキルです（intake-asana モード）。\n"
        f"Asana タスク GID: {task_gid}\n"
        f"snapshot: {snapshot_path.as_posix()}\n\n"
        "1. snapshot を読み bootstrap Handoff を生成\n"
        "2. bootstrap → dispatch（planning-pm）まで進める\n"
        "3. planning gate 到達後 --record-wait でダッシュボード反映\n"
    )


def ensure_snapshot(task_gid: str, *, dry_run: bool) -> Path:
    INTAKE_DIR.mkdir(parents=True, exist_ok=True)
    out = INTAKE_DIR / f"{task_gid}-snapshot.json"
    if dry_run:
        print(f"INTAKE  source={task_gid}  dry-run  snapshot={out.as_posix()}")
        return out
    cmd = [
        sys.executable,
        str(ROOT / "tools/intake_from_asana.py"),
        "--task",
        task_gid,
        "--out",
        str(out),
    ]
    r = subprocess.run(cmd, cwd=str(ROOT))
    if r.returncode != 0:
        raise SystemExit(r.returncode)
    return out


def dispatch_cursor(prompt: str) -> int:
    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        print("SKIP  CURSOR_API_KEY unset — use CLI baseline (auto_intake_runner.py)")
        return 0
    try:
        from cursor_sdk import Agent, AgentOptions, LocalAgentOptions  # type: ignore
    except ImportError:
        print("SKIP  cursor_sdk not installed — pip install cursor-sdk")
        return 0
    print("DISPATCH  cursor_sdk Agent.prompt starting…")
    result = Agent.prompt(
        prompt,
        AgentOptions(
            api_key=api_key,
            model="composer-2.5",
            local=LocalAgentOptions(cwd=str(ROOT)),
        ),
    )
    print(f"DISPATCH  cursor_sdk status={result.status}")
    if getattr(result, "result", None):
        print(str(result.result)[:500])
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Cursor SDK intake-asana PoC")
    p.add_argument("--task", required=True, metavar="GID")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("-y", "--yes", action="store_true")
    args = p.parse_args()

    dry_run = args.dry_run or not args.yes
    snapshot = ensure_snapshot(args.task, dry_run=dry_run)
    prompt = build_prompt(args.task, snapshot)
    if dry_run:
        print("DISPATCH  dry-run  prompt_preview:")
        print(prompt[:400])
        return 0
    return dispatch_cursor(prompt)


if __name__ == "__main__":
    sys.exit(main())
