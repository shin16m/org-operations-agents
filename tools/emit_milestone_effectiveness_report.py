#!/usr/bin/env python3
"""Emit MilestoneEffectivenessReport JSON + human-readable markdown summary.

Usage:
  python tools/emit_milestone_effectiveness_report.py `
    --checklist docs/verification/fixtures/milestone-readiness/m5-learning-loop.json `
    --tracker-gid <GID>
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / ".venv/Scripts/python.exe"
if not PY.is_file():
    PY = Path(sys.executable)


def _render_md(report: dict) -> str:
    lines = [
        f"# マイルストーン実効達成度 — {report.get('title')}",
        "",
        f"| 項目 | 値 |",
        f"|------|-----|",
        f"| milestone_id | `{report.get('milestone_id')}` |",
        f"| score | **{report.get('score')}** |",
        f"| status | `{report.get('status')}` |",
        f"| tracker_gid | `{report.get('tracker_gid', '')}` |",
        "",
    ]
    axes = report.get("axis_scores") or {}
    if axes:
        lines.extend(["## 軸スコア", ""])
        for k, v in axes.items():
            lines.append(f"- **{k}**: {v}")
        lines.append("")
    gaps = report.get("gaps") or []
    if gaps:
        lines.extend(["## ギャップ", ""])
        for g in gaps:
            lines.append(f"- [{g.get('severity', 'P2')}] `{g.get('check_id')}`: {g.get('message')}")
        lines.append("")
    follow = report.get("follow_up_candidates") or []
    if follow:
        lines.extend(["## フォローアップ候補", ""])
        for f in follow:
            lines.append(f"- **{f.get('title')}** ({f.get('department')}): {f.get('summary', '')}")
        lines.append("")
    lines.append(f"_generated_at: {report.get('generated_at')}_")
    return "\n".join(lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description="Emit milestone effectiveness report + markdown")
    p.add_argument("--checklist", required=True)
    p.add_argument("--tracker-gid", required=True)
    p.add_argument("--work-epic-gid", default=None)
    p.add_argument("--json-out", default=None, help="JSON path (default: milestone-reports/<gid>-readiness.json)")
    p.add_argument("--md-out", default=None, help="Markdown path (default: milestone-reports/<gid>-summary.md)")
    p.add_argument("--strict", action="store_true")
    args = p.parse_args()

    json_out = args.json_out or f"output/governance/milestone-reports/{args.tracker_gid}-readiness.json"
    md_out = args.md_out or f"output/governance/milestone-reports/{args.tracker_gid}-summary.md"

    cmd = [
        str(PY),
        str(ROOT / "tools/check_milestone_readiness.py"),
        "--checklist",
        args.checklist,
        "--tracker-gid",
        args.tracker_gid,
        "--out",
        json_out,
    ]
    if args.work_epic_gid:
        cmd.extend(["--work-epic-gid", args.work_epic_gid])
    if args.strict:
        cmd.append("--strict")

    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    json_path = ROOT / json_out
    if not json_path.is_file():
        print(r.stderr or r.stdout, file=sys.stderr)
        return r.returncode or 1

    report = json.loads(json_path.read_text(encoding="utf-8"))
    md_path = ROOT / md_out
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(_render_md(report), encoding="utf-8")

    print("wrote", json_path.relative_to(ROOT))
    print("wrote", md_path.relative_to(ROOT))
    print(
        f"MILESTONE_REPORT score={report.get('score')} status={report.get('status')}",
        file=sys.stderr,
    )
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
