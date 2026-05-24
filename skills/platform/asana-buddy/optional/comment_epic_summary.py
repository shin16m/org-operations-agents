#!/usr/bin/env python3
"""Post a human-friendly epic completion summary before marking the parent complete.

Usage:
  python comment_epic_summary.py --gid <PARENT_GID> --summary "..." --body-file summary.md -y
  python comment_epic_summary.py --gid <PARENT_GID> --body "..." -y
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
    format_signed_comment,
)

_ORCHESTRATOR = "workflow-orchestrator"
_SKILL = "skills/platform/workflow-orchestrator/SKILL.md"


def main() -> None:
    p = argparse.ArgumentParser(description="Post epic completion summary comment on parent task")
    p.add_argument("--gid", required=True, help="Parent epic task GID")
    p.add_argument("--summary", default=None, help="One-line summary (## 要約)")
    p.add_argument("--body", default=None, help="Markdown body (## 実施内容 等)")
    p.add_argument("--body-file", default=None, help="Read body from file")
    p.add_argument("--dry-run", action="store_true", help="Print comment only")
    p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    args = p.parse_args()

    body = args.body or ""
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    if not (body.strip() or (args.summary or "").strip()):
        p.error("--body, --body-file, or --summary is required")

    text = format_signed_comment(
        _ORCHESTRATOR,
        _SKILL,
        body,
        phase="complete",
        summary=args.summary,
    )

    if args.dry_run:
        print(console_safe(text))
        return

    if not args.yes:
        print(console_safe(f"タスク {args.gid} にエピック完了サマリを投稿しますか? (y/N): "), end="")
        if input().strip().lower() != "y":
            print("abort")
            sys.exit(0)

    load_env_from_dotfile()
    token = get_token()
    story = create_task_story(args.gid, text, token)
    print("posted_story", story.get("gid"), "task", args.gid)


if __name__ == "__main__":
    main()
