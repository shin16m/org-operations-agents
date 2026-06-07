#!/usr/bin/env python3
"""Create intake source Asana tasks from approved epic retrospective (R5).

Requires check_retrospective_intake_gate.py exit 0, unless --requester-approved
with non-empty --requester-notes (chat/session approval).

Usage:
  python tools/create_retrospective_intake_tasks.py --parent <EPIC_GID> --retro <epic-retro.json> -y
  python tools/create_retrospective_intake_tasks.py ... --requester-approved --requester-notes "..." -y
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPTIONAL = ROOT / "skills/platform/asana-buddy/optional"
if str(OPTIONAL) not in sys.path:
    sys.path.insert(0, str(OPTIONAL))

from agent_handler_asana import create_task, get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    console_safe,
    find_project_task_by_exact_name,
    resolve_project_with_fallback,
)

# Plain-language intros for known retro summaries (substring match).
_HUMAN_HINTS: list[tuple[str, str, str]] = [
    (
        "assign plan",
        "PM が Asana に作る「作業用サブタスク」の計画（assign plan）に、振り返り用の `[retro]` サブタスクを **自動で一緒に作る** ようにする改善です。今は PM が手動で追加する必要があります。",
        "Phase 2: `pm_assign_subtasks` / assign plan JSON へ `[retro]` 行を同梱。",
    ),
    (
        "stories",
        "レトロ承認時に、依頼者が Asana のコメント欄に書いた意見を **自動で読み取り**、起票する intake タスクの説明に反映する改善です。今は `--requester-notes` を手入力する必要があります。",
        "Asana stories API で承認サブのコメントをパース → `## 依頼者コメント` へ注入。",
    ),
    (
        "人間向け",
        "Asana タスクの「説明（notes）」が専門用語中心で、**このプロジェクトに詳しくない人**が読んで意図を把握しづらい問題への改善です。",
        "AI/エージェント向け詳細は `## 背景・用語` に分離し、`## 依頼者向け` を必須化（comment / Handoff / intake 共通）。",
    ),
]


def _human_blocks(summary: str) -> tuple[str, str]:
    for key, human, tech in _HUMAN_HINTS:
        if key.lower() in (summary or "").lower():
            return human, tech
    human = (
        f"エピック完了後の振り返りで挙がった改善案です: **{summary}**。"
        " org-operations-agents は AI エージェントの作業手順を定義するリポジトリです。"
    )
    tech = summary or ""
    return human, tech


def _gate_ok(parent: str) -> bool:
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools/check_retrospective_intake_gate.py"), "--parent", parent],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return r.returncode == 0


def _build_notes(
    *,
    parent_gid: str,
    candidate: dict,
    requester: str,
) -> str:
    summary = candidate.get("summary") or ""
    human, tech = _human_blocks(summary)
    return "\n".join(
        [
            "## 依頼者向け（人間が最初に読む）",
            "",
            human,
            "",
            "## 背景・用語（エージェント / 実装者向け）",
            "",
            tech,
            "",
            "## ソース",
            "",
            f"- 元エピック GID: `{parent_gid}`",
            f"- レトロ出典タスク: `{candidate.get('source_task_gid', '（依頼者追加分）')}`",
            f"- 出典 agent: `{candidate.get('source_agent', 'requester')}`",
            "",
            "## 改善概要（一行）",
            "",
            summary,
            "",
            "## 依頼者コメント（承認時）",
            "",
            requester,
            "",
            "## 次のステップ",
            "",
            "1. 和久桶さんに「intake」と依頼（workflow-orchestrator）",
            "2. 企画 gate 承認後に execution 系で実装",
            "",
            "関連 SSOT: `docs/design/task-retrospective-ssot.md`",
        ]
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Create intake tasks from epic retro")
    p.add_argument("--parent", required=True, help="Epic GID")
    p.add_argument("--retro", type=Path, required=True)
    p.add_argument("--requester-notes", default="", help="## 依頼者コメント（承認時）")
    p.add_argument(
        "--requester-approved",
        action="store_true",
        help="Skip Asana gate when requester approved in chat (--requester-notes required)",
    )
    p.add_argument(
        "--add-candidate",
        action="append",
        default=[],
        metavar="SUMMARY",
        help="Extra intake candidate (e.g. requester feedback at approval)",
    )
    p.add_argument("-y", action="store_true")
    args = p.parse_args()

    requester = (args.requester_notes or "").strip()
    gate_ok = _gate_ok(args.parent)
    if not gate_ok:
        if args.requester_approved and requester:
            print("note: using --requester-approved (chat/session); Asana gate not complete", file=sys.stderr)
        else:
            print(
                "intake gate not approved — complete 【承認】レトロ改善候補 in Asana UI, "
                "or pass --requester-approved --requester-notes for chat approval.",
                file=sys.stderr,
            )
            return 1

    data = json.loads(args.retro.read_text(encoding="utf-8"))
    cands = list(data.get("intake_candidates") or [])
    for extra in args.add_candidate or []:
        text = extra.strip()
        if text:
            cands.append(
                {
                    "id": f"requester-{len(cands) + 1}",
                    "source_task_gid": "",
                    "source_agent": "requester",
                    "summary": text,
                }
            )

    if not cands:
        print("no intake candidates — nothing to create")
        return 0

    if not requester:
        requester = "（Asana 承認サブのコメント、または --requester-notes を使用）"

    load_env_from_dotfile()
    token = get_token()
    project_gid = resolve_project_with_fallback(None)

    created: list[str] = []
    for c in cands:
        summary = c.get("summary") or "改善"
        title = f"【intake】{summary[:72]}"
        existing_gid = find_project_task_by_exact_name(project_gid, title, token)
        if existing_gid:
            print("exists_intake_task", existing_gid, console_safe(title[:60]))
            created.append(existing_gid)
            continue
        notes = _build_notes(parent_gid=args.parent, candidate=c, requester=requester)
        if not args.y:
            print(console_safe(f"would create {title!r}"))
            continue
        task = create_task(project_gid, title, notes, token)
        created.append(str(task.get("gid")))
        print("created_intake_task", task.get("gid"), console_safe(title[:60]))

    print(json.dumps({"created": created}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
