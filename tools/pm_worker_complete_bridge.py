#!/usr/bin/env python3
"""Kick product-manager to complete a worker sub after signed comment (Phase C).

Usage:
  python tools/pm_worker_complete_bridge.py --parent <PM_CHILD> --sub <WORKER_SUB> --department development --dry-run
  python tools/pm_worker_complete_bridge.py --parent <PM_CHILD> --sub <WORKER_SUB> --department development -y
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
TOOLS = ROOT / "tools"
for p in (str(ASANA_OPT), str(TOOLS)):
    if p not in sys.path:
        sys.path.insert(0, p)

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import fetch_task, parse_task_assignment  # noqa: E402
from cursor_sdk_kick import kick_prompt  # noqa: E402
from execution_resume_scan import has_agent_comment  # noqa: E402
from pm_emit_worker_prompt import DEPT_PM  # noqa: E402


def build_bridge_prompt(
    *,
    pm_child_gid: str,
    worker_sub_gid: str,
    department: str,
    worker_slug: str,
) -> str:
    pm_slug = DEPT_PM.get(department, "product-manager")
    return (
        f"あなたは {pm_slug} スキルです（pm_worker_complete_bridge kick）。\n"
        f"PM 子 GID: {pm_child_gid}\n"
        f"worker サブ GID: {worker_sub_gid}\n"
        f"worker slug: {worker_slug}\n\n"
        "【やること — この 1 手のみ】\n"
        f"1. fetch_task.py --gid {worker_sub_gid} --show-assignee で worker 署名 comment を確認\n"
        f"2. complete_task.py --gid {worker_sub_gid} -y\n"
        "3. セッション終了（他サブに着手禁止 · 次 worker dispatch 禁止）\n\n"
        "【禁止】\n"
        "- 要件・設計・コードの作成\n"
        "- 【レビュー】/【承認】サブの complete\n"
        "- 次 worker の cursor_worker_dispatch\n"
    )


def run_bridge(
    *,
    pm_child_gid: str,
    worker_sub_gid: str,
    department: str,
    dry_run: bool,
    kick: bool,
) -> int:
    load_env_from_dotfile()
    token = get_token()
    pm_slug = DEPT_PM.get(department)
    if not pm_slug:
        print(f"error: unknown department {department!r}", file=sys.stderr)
        return 2

    notes = fetch_task(worker_sub_gid, token).get("notes") or ""
    worker_slug = parse_task_assignment(str(notes)).get("assignee") or ""
    if not worker_slug:
        print(f"error: no assignee on sub={worker_sub_gid}", file=sys.stderr)
        return 2
    if not has_agent_comment(worker_sub_gid, worker_slug, token):
        print(
            f"SKIP  no signed comment  sub={worker_sub_gid}  worker={worker_slug}",
            file=sys.stderr,
        )
        return 1

    prompt = build_bridge_prompt(
        pm_child_gid=pm_child_gid,
        worker_sub_gid=worker_sub_gid,
        department=department,
        worker_slug=worker_slug,
    )
    print(
        f"BRIDGE  parent={pm_child_gid}  sub={worker_sub_gid}  "
        f"department={department}  worker={worker_slug}"
    )
    if dry_run or not kick:
        print(prompt[:600])
        if not kick:
            print("KICK  dry-run  (use -y to execute)")
        return 0

    return kick_prompt(
        prompt,
        cwd=ROOT,
        label="KICK",
        no_api_key_exit=0,
        no_sdk_exit=0,
        hint_manual="PM complete worker sub manually",
    )


def main() -> int:
    p = argparse.ArgumentParser(description="PM bridge: complete worker sub after comment")
    p.add_argument("--parent", required=True, help="PM child task GID")
    p.add_argument("--sub", required=True, help="Worker subtask GID")
    p.add_argument("--department", required=True, choices=sorted(DEPT_PM))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("-y", "--yes", action="store_true", help="Execute SDK kick")
    args = p.parse_args()

    kick = args.yes and not args.dry_run
    return run_bridge(
        pm_child_gid=args.parent,
        worker_sub_gid=args.sub,
        department=args.department,
        dry_run=args.dry_run and not kick,
        kick=kick,
    )


if __name__ == "__main__":
    sys.exit(main())
