#!/usr/bin/env python3
"""Close an intake-asana source task after bootstrap epic creation.

Posts a signed comment linking to the new epic, then marks the source task complete.

Usage:
  python close_intake_source_task.py --source 1215082835252589 --epic 1215085684107323 -y
  python close_intake_source_task.py --source 1215082835252589 --epic 1215085684107323 --dry-run
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
    console_safe,
    create_task_story,
    fetch_task,
    format_signed_comment,
    set_task_completed,
)


def epic_permalink(epic_gid: str, token: str, epic_url: str | None) -> str:
    if epic_url:
        return epic_url.strip()
    data = fetch_task(epic_gid, token)
    return (data.get("permalink_url") or "").strip() or f"https://app.asana.com/0/0/0/{epic_gid}"


def build_body(epic_gid: str, epic_link: str) -> str:
    return (
        "## 依頼者向け\n"
        "intake 元タスクとして org-ops エピックを起票しました。"
        "以降の進捗は新エピックで追跡してください。\n\n"
        "## 新エピック\n"
        f"- URL: {epic_link}\n"
        f"- GID: `{epic_gid}`\n"
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Comment + complete intake-asana source task")
    p.add_argument("--source", required=True, help="Source task GID (intake-asana origin)")
    p.add_argument("--epic", required=True, help="New epic parent task GID")
    p.add_argument("--epic-url", default=None, help="Epic permalink (fetched if omitted)")
    p.add_argument(
        "--no-complete",
        action="store_true",
        help="Post comment only; do not mark source complete",
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("-y", "--yes", action="store_true")
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()
    epic_link = epic_permalink(args.epic, token, args.epic_url)
    body = build_body(args.epic, epic_link)
    text = format_signed_comment(
        "workflow-orchestrator",
        "skills/platform/workflow-orchestrator/SKILL.md",
        body,
        phase="complete",
        summary="intake 元タスク → 新エピックへ引き継ぎ",
    )

    if args.dry_run:
        print(console_safe(text))
        print("would_complete", not args.no_complete, "source", args.source)
        return

    if not args.yes:
        print(
            console_safe(
                f"ソース {args.source} にコメント"
                + ("" if args.no_complete else " → 完了")
                + " しますか? (y/N): "
            ),
            end="",
        )
        if input().strip().lower() != "y":
            print("abort")
            sys.exit(0)

    story = create_task_story(args.source, text, token)
    print("posted_story", story.get("gid"), "source", args.source)

    if not args.no_complete:
        data = set_task_completed(args.source, True, token)
        print("updated", data.get("gid"), "completed=", data.get("completed"))


if __name__ == "__main__":
    main()
