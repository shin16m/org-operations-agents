#!/usr/bin/env python3
"""Create intake source Asana tasks from approved epic retrospective (R5).

Requires check_retrospective_intake_gate.py exit 0.

Usage:
  python tools/create_retrospective_intake_tasks.py --parent <EPIC_GID> --retro <epic-retro.json> -y
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
from asana_program_common import console_safe, resolve_project_with_fallback  # noqa: E402


def _gate_ok(parent: str) -> bool:
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools/check_retrospective_intake_gate.py"), "--parent", parent],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return r.returncode == 0


def main() -> int:
    p = argparse.ArgumentParser(description="Create intake tasks from epic retro")
    p.add_argument("--parent", required=True, help="Epic GID")
    p.add_argument("--retro", type=Path, required=True)
    p.add_argument("--requester-notes", default="", help="Override ## 依頼者コメント")
    p.add_argument("-y", action="store_true")
    args = p.parse_args()

    if not _gate_ok(args.parent):
        print("intake gate not approved — complete 【承認】レトロ改善候補 in Asana UI first.", file=sys.stderr)
        return 1

    data = json.loads(args.retro.read_text(encoding="utf-8"))
    cands = data.get("intake_candidates") or []
    if not cands:
        print("no intake candidates — nothing to create")
        return 0

    load_env_from_dotfile()
    token = get_token()
    project_gid = resolve_project_with_fallback(None)

    requester = (args.requester_notes or "").strip()
    if not requester:
        requester = "（Asana 承認サブのコメントを手動で追記する場合は --requester-notes を使用）"

    created: list[str] = []
    for c in cands:
        title = f"【intake候補】{c.get('summary', '改善')[:80]}"
        notes = "\n".join(
            [
                "## ソース",
                "",
                f"- エピック GID: `{args.parent}`",
                f"- 出典タスク: `{c.get('source_task_gid')}`",
                f"- 出典 agent: `{c.get('source_agent')}`",
                "",
                "## 改善概要",
                "",
                c.get("summary") or "",
                "",
                "## 依頼者コメント",
                "",
                requester,
                "",
                "## 次のステップ",
                "",
                "和久桶さん intake（workflow-orchestrator）から新エピックへ。",
            ]
        )
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
