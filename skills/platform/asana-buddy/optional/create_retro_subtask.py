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


def retro_subtask_title(worker: str) -> str:
    return f"[retro] {worker} — 所感・改善案"


def build_retro_subtask_notes(*, department: str, assignee: str) -> str:
    notes = assemble_subtask_notes(
        background="タスク完了前レトロ（task-retrospective-ssot）。",
        summary="うまくいった点 / 改善したい点 / 次エピック候補を記載。",
        done_when="3 項目記載後 comment_task → PM が worker 本番サブ complete 可。",
        department=department,
        assignee=assignee,
        status="assigned",
    )
    return notes + "\n\n## 記入テンプレ\n\n- **うまくいった点:** \n- **改善したい点:** \n- **次エピック候補:** \n"


def ensure_retro_subtask(
    parent_gid: str,
    worker: str,
    *,
    department: str,
    token: str,
) -> tuple[str, str | None]:
    """Create nested [retro] sub if missing. Returns (status, gid)."""
    title = retro_subtask_title(worker)
    for sub in list_subtasks(parent_gid, token):
        if (sub.get("name") or "").strip() == title:
            state = "exists_completed" if sub.get("completed") else "exists_open"
            return state, str(sub.get("gid") or "") or None

    notes = build_retro_subtask_notes(department=department, assignee=worker)
    sub = create_subtask(parent_gid, title, notes, token)
    return "created", str(sub.get("gid") or "") or None


def main() -> None:
    p = argparse.ArgumentParser(description="Create [retro] nested subtask")
    p.add_argument("--parent", required=True, help="Worker subtask GID")
    p.add_argument("--worker", required=True, help="Worker slug")
    p.add_argument("--department", default="governance")
    p.add_argument("-y", action="store_true")
    args = p.parse_args()

    title = retro_subtask_title(args.worker)
    load_env_from_dotfile()
    token = get_token()

    if not args.y:
        print(console_safe(f"Create {title!r} under {args.parent}? (y/N): "), end="")
        if input().strip().lower() != "y":
            return

    status, gid = ensure_retro_subtask(
        args.parent,
        args.worker,
        department=args.department,
        token=token,
    )
    if status.startswith("exists_"):
        state = status.removeprefix("exists_")
        print(f"exists_{state}", gid, console_safe(title))
        return
    print("created_retro_subtask", gid, console_safe(title))


if __name__ == "__main__":
    main()
