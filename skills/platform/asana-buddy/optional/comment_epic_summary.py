#!/usr/bin/env python3
"""Post a human-friendly epic completion summary before marking the parent complete.

Usage:
  python comment_epic_summary.py --gid <PARENT_GID> --summary "..." --body-file summary.md -y
  python comment_epic_summary.py --gid <PARENT_GID> --body "..." -y
  python comment_epic_summary.py --gid <PARENT_GID> --render-template --should-gaps-json gaps.json -y
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_ROOT = _SCRIPT_DIR.parents[3]
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
_DEFAULT_TEMPLATE = _ROOT / "docs/design/epic-completion-summary-template.md"


def _table_should_gaps(gaps: list[dict]) -> str:
    if not gaps:
        return "（Should 未達なし — すべて pass）"
    lines = ["| AC | 優先度 | 内容 | 検証 |", "|----|--------|------|------|"]
    for g in gaps:
        ac = g.get("ac_id", "—")
        pri = g.get("priority", "Should")
        summary = g.get("summary", "")
        cmd = g.get("verify_command", "—")
        lines.append(f"| {ac} | {pri} | {summary} | `{cmd}` |")
    return "\n".join(lines)


def render_template_body(
    *,
    should_gaps: list[dict],
    verify_commands: list[str],
    next_actions: list[str],
    completion_level: str = "~80%",
    must_pass_rate: str = "100%",
    should_pass_rate: str = "60%+",
    artifacts: list[str] | None = None,
    sla_summary: str | None = None,
    polish_summary: str | None = None,
    known_limitations: str | None = None,
) -> str:
    artifacts_list = "\n".join(f"- `{a}`" for a in (artifacts or [])) or "（Epic 子の DeptWorkComplete 参照）"
    verify_list = "\n".join(f"- `{c}`" for c in verify_commands) or "（README の起動コマンド 1 本）"
    actions_list = "\n".join(f"- {a}" for a in next_actions) or "（なし）"
    gaps_table = _table_should_gaps(should_gaps)
    extra_100 = ""
    if completion_level.strip().startswith("100"):
        extra_100 = f"""
## SLA 達成
{sla_summary or "（要件 §SLA 参照）"}

## UX polish
{polish_summary or "（full-ui: a11y · エラー · 空状態 pass）"}

## 既知制限
{known_limitations or "（なし）"}
"""

    return f"""## 実施内容
- 本 Epic の execution 系子タスクを完了し、成果物をリポジトリに保存しました
- 完成度: **{completion_level}**（Must AC {must_pass_rate} · Should {should_pass_rate}）

## 成果物
{artifacts_list}

## Should AC 未達一覧
{gaps_table}

## 検証コマンド（依頼者が README のみで再現）
{verify_list}

## 次のアクション
{actions_list}

## 次の状態
- 依頼者が上記検証コマンドで確認後、Epic を complete してください
{extra_100}"""


def main() -> None:
    p = argparse.ArgumentParser(description="Post epic completion summary comment on parent task")
    p.add_argument("--gid", required=True, help="Parent epic task GID")
    p.add_argument("--summary", default=None, help="One-line summary (## 要約)")
    p.add_argument("--body", default=None, help="Markdown body (## 実施内容 等)")
    p.add_argument("--body-file", default=None, help="Read body from file")
    p.add_argument("--render-template", action="store_true", help="Build body from SSOT template")
    p.add_argument("--should-gaps-json", default=None, help="JSON array of Should gap objects")
    p.add_argument("--verify-command", action="append", default=[], help="Verify command (repeatable)")
    p.add_argument("--next-action", action="append", default=[], help="Next action (repeatable)")
    p.add_argument("--artifact", action="append", default=[], help="Artifact path (repeatable)")
    p.add_argument("--completion-level", default="~80%")
    p.add_argument("--must-pass-rate", default="100%")
    p.add_argument("--should-pass-rate", default="60%+")
    p.add_argument("--sla-summary", default=None, help="SLA 達要一行（100% 時）")
    p.add_argument("--polish-summary", default=None, help="UX polish 達要一行（100% 時）")
    p.add_argument("--known-limitations", default=None, help="既知制限（100% 時）")
    p.add_argument("--dry-run", action="store_true", help="Print comment only")
    p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    args = p.parse_args()

    body = args.body or ""
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    if args.render_template:
        gaps: list[dict] = []
        if args.should_gaps_json:
            gaps = json.loads(Path(args.should_gaps_json).read_text(encoding="utf-8"))
        body = render_template_body(
            should_gaps=gaps,
            verify_commands=list(args.verify_command or []),
            next_actions=list(args.next_action or []),
            completion_level=args.completion_level,
            must_pass_rate=args.must_pass_rate,
            should_pass_rate=args.should_pass_rate,
            artifacts=list(args.artifact or []),
            sla_summary=args.sla_summary,
            polish_summary=args.polish_summary,
            known_limitations=args.known_limitations,
        )
    if not (body.strip() or (args.summary or "").strip()):
        p.error("--body, --body-file, --render-template, or --summary is required")

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
