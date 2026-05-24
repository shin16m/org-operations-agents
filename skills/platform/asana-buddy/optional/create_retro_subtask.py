#!/usr/bin/env python3
"""Create [retro] nested subtask under a worker subtask.

Usage:
  python create_retro_subtask.py --parent <worker_sub_gid> --worker ssot-implementer -y
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    assemble_subtask_notes,
    console_safe,
    create_subtask,
    list_subtasks,
)


def main() -> None:
    p = argparse.ArgumentParser(description="Create [retro] nested subtask")
    p.add_argument("--parent", required=True, help="Worker subtask GID")
    p.add_argument("--worker", required=True, help="Worker slug")
    p.add_argument("--department", default="governance")
    p.add_argument("-y", action="store_true")
    args = p.parse_args()

    title = f"[retro] {args.worker} — 所感・改善案"
    load_env_from_dotfile()
    token = get_token()

    for sub in list_subtasks(args.parent, token):
        if (sub.get("name") or "").strip() == title and not sub.get("completed"):
            print("exists_open", sub.get("gid"), console_safe(title))
            return

    notes = assemble_subtask_notes(
        background="タスク完了前レトロ（task-retrospective-ssot）。",
        summary="うまくいった点 / 改善したい点 / 次エピック候補を記載。",
        done_when="3 項目記載後 comment_task → PM が worker 本番サブ complete 可。",
        department=args.department,
        assignee=args.worker,
        status="assigned",
    )
    notes += "\n\n## 記入テンプレ\n\n- **うまくいった点:** \n- **改善したい点:** \n- **次エピック候補:** \n"

    if not args.y:
        print(console_safe(f"Create {title!r} under {args.parent}? (y/N): "), end="")
        if input().strip().lower() != "y":
            return

    sub = create_subtask(args.parent, title, notes, token)
    print("created_retro_subtask", sub.get("gid"), console_safe(title))


if __name__ == "__main__":
    main()
