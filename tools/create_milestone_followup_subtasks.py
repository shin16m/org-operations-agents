#!/usr/bin/env python3
"""Create follow-up Asana subtasks from MilestoneEffectivenessReport gaps.

Default is dry-run (print only). Use --apply -y to create under --parent.

Usage:
  python tools/create_milestone_followup_subtasks.py `
    --report output/governance/milestone-reports/<gid>-readiness.json `
    --parent <EPIC_GID> --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPTIONAL = ROOT / "skills/platform/asana-buddy/optional"
if str(OPTIONAL) not in sys.path:
    sys.path.insert(0, str(OPTIONAL))

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import assemble_subtask_notes, console_safe, create_subtask  # noqa: E402


def _dept_for_severity(sev: str) -> str:
    if sev in ("P0", "P1"):
        return "development"
    return "governance"


def main() -> int:
    p = argparse.ArgumentParser(description="Create milestone follow-up subtasks from report")
    p.add_argument("--report", required=True, help="MilestoneEffectivenessReport JSON path")
    p.add_argument("--parent", required=True, help="Parent epic GID for new subtasks")
    p.add_argument("--min-score", type=float, default=80.0, help="Skip if report score >= this")
    p.add_argument("--apply", action="store_true", help="Actually create Asana subtasks (default: dry-run)")
    p.add_argument("-y", action="store_true", help="Skip confirmation when --apply")
    args = p.parse_args()

    report_path = ROOT / args.report
    if not report_path.is_file():
        print(f"report not found: {report_path}", file=sys.stderr)
        return 2

    report = json.loads(report_path.read_text(encoding="utf-8"))
    score = float(report.get("score") or 0)
    if score >= args.min_score:
        print(f"SKIP  score={score} >= min_score={args.min_score}")
        return 0

    candidates = report.get("follow_up_candidates") or []
    if not candidates:
        for gap in report.get("gaps") or []:
            candidates.append(
                {
                    "title": f"[milestone-fix] {gap.get('check_id')}",
                    "department": _dept_for_severity(str(gap.get("severity") or "P2")),
                    "summary": gap.get("message", ""),
                }
            )

    if not candidates:
        print("no follow-up candidates")
        return 0

    dry = not bool(args.apply)
    if args.apply and not args.y:
        print("use --apply -y to create subtasks", file=sys.stderr)
        return 2

    load_env_from_dotfile()
    token = get_token()
    created = 0
    for cand in candidates:
        title = str(cand.get("title") or "milestone follow-up")
        dept = str(cand.get("department") or "governance")
        summary = str(cand.get("summary") or "")
        notes = assemble_subtask_notes(
            background=f"マイルストーン readiness 未達（score={score}）に伴うフォローアップ。",
            summary=summary,
            done_when="ギャップ解消を verification 記録で確認。governance または development review passed。",
            pillar=dept,
            department=dept,
        )
        if dry:
            print("DRY-RUN  subtask", console_safe(title), dept)
            continue
        sub = create_subtask(args.parent, title, notes, token)
        gid = sub.get("gid")
        print("created_subtask", gid, console_safe(title))
        created += 1

    print(f"followup  count={len(candidates)}  created={created}  dry_run={dry}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
