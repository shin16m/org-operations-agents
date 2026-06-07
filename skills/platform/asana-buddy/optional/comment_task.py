#!/usr/bin/env python3
"""Post a signed agent-work-record comment (story) on an Asana task."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_comment_guard import validate_comment_agent  # noqa: E402
from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    agent_work_comment_to_text,
    build_human_comment_body,
    console_safe,
    create_task_story,
    format_signed_comment,
    load_agent_work_comment,
    validate_comment_body_not_legacy_task_notes,
)


def main() -> None:
    p = argparse.ArgumentParser(description="Post signed agent comment on Asana task")
    p.add_argument("--gid", default=None, help="Task GID (required unless --from-json)")
    p.add_argument("--agent", default=None, help="agent-registry slug")
    p.add_argument("--skill", default=None, help="Skill path, e.g. skills/development/developer/SKILL.md")
    p.add_argument("--summary", default=None, help="Short summary (also ## 要約)")
    p.add_argument("--body", default=None, help="Comment body markdown")
    p.add_argument("--body-file", default=None, help="Read body from file")
    p.add_argument("--phase", default="complete", choices=("start", "complete"))
    p.add_argument("--model", default=None, help="Optional LLM name")
    p.add_argument("--artifact", action="append", default=[], help="Artifact path (repeatable)")
    p.add_argument("--action", action="append", default=[], help="実施内容 bullet (repeatable; builds --body)")
    p.add_argument("--reason", default=None, help="判断・理由（レビュアー/PM 向け）")
    p.add_argument("--next-state", default=None, help="次の状態（1 段落）")
    p.add_argument("--from-json", metavar="PATH", help="AgentWorkComment v1.0 JSON")
    p.add_argument("--dry-run", action="store_true", help="Print comment only")
    p.add_argument(
        "--skip-assignee-check",
        action="store_true",
        help="Skip notes 担当: vs --agent validation (dryrun teardown only)",
    )
    p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    args = p.parse_args()

    if args.from_json:
        data = load_agent_work_comment(args.from_json)
        task_gid = data["task_gid"]
        text = agent_work_comment_to_text(data)
    else:
        if not args.gid or not args.agent or not args.skill:
            p.error("--gid, --agent, and --skill are required (or use --from-json)")
        body = args.body or ""
        if args.body_file:
            body = Path(args.body_file).read_text(encoding="utf-8")
        if not body.strip() and args.action:
            body = build_human_comment_body(
                actions=args.action,
                reason=args.reason,
                artifacts=args.artifact or None,
                next_state=args.next_state,
            )
        if body.strip() and not args.action:
            legacy_err = validate_comment_body_not_legacy_task_notes(body)
            if legacy_err:
                print(f"ERROR: {legacy_err}", file=sys.stderr)
                sys.exit(2)
        if not (body.strip() or (args.summary or "").strip()):
            p.error("--body, --body-file, --summary, or --action is required")
        task_gid = args.gid
        text = format_signed_comment(
            args.agent,
            args.skill,
            body,
            phase=args.phase,
            model=args.model,
            summary=args.summary,
            artifacts=args.artifact or None,
        )

    if args.dry_run:
        print(console_safe(text))
        return

    load_env_from_dotfile()
    token = get_token()

    if not args.from_json and not args.skip_assignee_check:
        err = validate_comment_agent(
            task_gid=task_gid,
            agent=str(args.agent),
            skill=str(args.skill),
            token=token,
        )
        if err:
            print(f"ERROR: {err}", file=sys.stderr)
            sys.exit(4)

    if not args.yes:
        print(console_safe(f"タスク {task_gid} にコメントを投稿しますか? (y/N): "), end="")
        if input().strip().lower() != "y":
            print("abort")
            sys.exit(0)

    story = create_task_story(task_gid, text, token)
    print("posted_story", story.get("gid"), "task", task_gid)


if __name__ == "__main__":
    main()
