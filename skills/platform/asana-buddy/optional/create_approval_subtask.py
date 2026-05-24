#!/usr/bin/env python3
"""Create a human-approval subtask under a parent Asana task.

Shared helper for planning gate, PM assign review gate, and similar flows.

Usage:
  python create_approval_subtask.py --parent <GID> --title "【承認】..." -y
  python create_approval_subtask.py --parent <GID> --marker "【レビュー】" --notes-file body.md -y
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import requests  # noqa: E402

from agent_handler_asana import ASANA_BASE, get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import console_safe, list_subtasks, set_assignee_type_human  # noqa: E402


def _create_subtask(parent_gid: str, title: str, notes: str, token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        f"{ASANA_BASE}/tasks/{parent_gid}/subtasks",
        json={"data": {"name": title, "notes": notes}},
        headers=headers,
    )
    r.raise_for_status()
    return r.json()["data"]


def main() -> None:
    p = argparse.ArgumentParser(description="Create human-approval subtask")
    p.add_argument("--parent", required=True, help="Parent task GID")
    p.add_argument("--title", default=None, help="Subtask title (required unless --marker only)")
    p.add_argument(
        "--marker",
        default=None,
        help="If --title omitted, use marker + suffix as title",
    )
    p.add_argument("--title-suffix", default="承認", help="Used with --marker when --title omitted")
    p.add_argument("--notes", default=None)
    p.add_argument("--notes-file", default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("-y", "--yes", action="store_true")
    args = p.parse_args()

    title = (args.title or "").strip()
    if not title:
        marker = (args.marker or "【承認】").strip()
        title = f"{marker}{args.title_suffix}"

    notes = args.notes or ""
    if args.notes_file:
        notes = Path(args.notes_file).read_text(encoding="utf-8")

    if not notes.strip():
        notes = (
            "## 依頼者向け\n\n"
            "内容を確認し、問題なければ **このサブタスクを完了**してください（完了 = 承認）。\n\n"
            "差し戻しは本サブを未完了のまま、親タスクにコメントで指摘してください。\n"
        )

    if args.dry_run:
        print(console_safe(f"would create title={title!r} under parent={args.parent}"))
        return

    load_env_from_dotfile()
    token = get_token()

    for sub in list_subtasks(args.parent, token):
        if (sub.get("name") or "").strip() == title and not sub.get("completed"):
            print("exists_open", sub.get("gid"), console_safe(title[:60]))
            return

    if not args.yes:
        print(console_safe(f"親 {args.parent} に {title!r} を作成しますか? (y/N): "), end="")
        if input().strip().lower() != "y":
            print("abort")
            sys.exit(0)

    sub = _create_subtask(args.parent, title, notes, token)
    set_assignee_type_human(sub.get("gid", ""), token)
    print("created_approval_subtask", sub.get("gid"), console_safe(title[:60]))


if __name__ == "__main__":
    main()
