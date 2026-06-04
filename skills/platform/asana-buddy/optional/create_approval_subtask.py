#!/usr/bin/env python3
"""Create a human-approval subtask under a parent Asana task.

Shared helper for planning gate, PM assign review gate, and similar flows.

Usage:
  python create_approval_subtask.py --parent <GID> --title "【承認】..." -y
  python create_approval_subtask.py --parent <GID> --marker "【レビュー】" --notes-file body.md -y
"""
from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = Path(__file__).resolve().parents[4]
_ORG_OS_SRC = _REPO_ROOT / "products/org-os/src"
for p in (_SCRIPT_DIR, _ORG_OS_SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import requests  # noqa: E402

from agent_handler_asana import ASANA_BASE, get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    assign_user,
    console_safe,
    create_task_story_html,
    html_user_mention_tag,
    human_approver_gid,
    list_subtasks,
    set_assignee_type_human,
)
from org_os import syscall  # noqa: E402
from org_os.asana_client import resolve_epic_gid  # noqa: E402
from org_os.constants import SUSPEND_REASON_APPROVAL  # noqa: E402


def _create_subtask(parent_gid: str, title: str, notes: str, token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        f"{ASANA_BASE}/tasks/{parent_gid}/subtasks",
        json={"data": {"name": title, "notes": notes}},
        headers=headers,
    )
    r.raise_for_status()
    return r.json()["data"]


def _post_approval_mention(sub_gid: str, human_gid: str, title: str, token: str) -> None:
    """Post @-mention via html_text (plain text `<@gid>` does not notify)."""
    mention = html_user_mention_tag(human_gid)
    safe_title = html.escape(title)
    # Stories allow: body, strong, em, u, s, code, ol, ul, li, a, blockquote, pre — NOT br/p/h*.
    html_body = (
        "<body>"
        "<strong>承認依頼</strong> "
        f"{mention} "
        f"<strong>{safe_title}</strong> "
        "内容を確認し、問題なければ <strong>このサブタスクを完了</strong>してください（完了 = 承認）。 "
        "差し戻しは本サブを未完了のまま、親タスクにコメントで指摘してください。"
        "</body>"
    )
    create_task_story_html(sub_gid, html_body, token)


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
    sub_gid = str(sub.get("gid") or "")
    set_assignee_type_human(sub_gid, token)

    human_gid = human_approver_gid()
    if human_gid:
        if assign_user(sub_gid, human_gid, token):
            print(f"assigned_human {sub_gid} {human_gid}")
    else:
        print(
            "警告: ASANA_DEFAULT_HUMAN_APPROVER_GID 未設定。assignee は手動設定してください。",
            file=sys.stderr,
        )

    try:
        epic_gid = resolve_epic_gid(args.parent, token)
        suspend_reason = (
            SUSPEND_REASON_APPROVAL
            if epic_gid == str(args.parent)
            else "Human Review"
        )
        result = syscall.suspend(
            epic_gid,
            suspend_reason,
            ref=sub_gid,
        )
        print(
            f"parent_syscall_suspend epic={epic_gid} wait_target={args.parent} "
            f"os_state={result['os_state']} reason={result['suspend_reason']}"
        )
    except (requests.HTTPError, ValueError, RuntimeError) as exc:
        print(
            f"警告: 親 syscall.suspend 失敗 parent={args.parent}: {exc}",
            file=sys.stderr,
        )

    if human_gid:
        try:
            _post_approval_mention(sub_gid, human_gid, title, token)
            print(f"mention_posted sub={sub_gid} user={human_gid}")
        except requests.HTTPError as exc:
            print(
                f"警告: @mention 投稿失敗 sub={sub_gid}: {exc}",
                file=sys.stderr,
            )

    print("created_approval_subtask", sub_gid, console_safe(title[:60]))


if __name__ == "__main__":
    main()
