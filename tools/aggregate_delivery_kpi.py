#!/usr/bin/env python3
"""Aggregate delivery KPIs from worker retrospectives and qa verification JSON.

SSOT: docs/design/delivery-completion-standard.md (KPI section)

Usage:
  python tools/aggregate_delivery_kpi.py [--parent EPIC_GID] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETRO_DIR = ROOT / "output/platform/retrospectives"
REVIEW_DIR = ROOT / "output/development/reviews"
OPTIONAL = ROOT / "skills/platform/asana-buddy/optional"
if str(OPTIONAL) not in sys.path:
    sys.path.insert(0, str(OPTIONAL))

PASSED = frozenset({"passed", "passed_with_notes"})
TASK_GID_FROM_NAME = re.compile(r"^(\d+)")


def _task_gid_from_filename(path: Path) -> str | None:
    m = TASK_GID_FROM_NAME.match(path.stem)
    return m.group(1) if m else None


def _load_verification_reviews(
    *, task_gids: set[str] | None
) -> tuple[list[dict], dict[str, list[dict]]]:
    """Return flat list and per-task_gid grouped verification reviews (first + fixes)."""
    if not REVIEW_DIR.is_dir():
        return [], {}

    by_task: dict[str, list[dict]] = {}
    for path in sorted(REVIEW_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if data.get("review_kind") != "verification":
            continue
        gid = _task_gid_from_filename(path)
        if not gid:
            continue
        if task_gids is not None and gid not in task_gids:
            continue
        entry = {"path": str(path), "status": data.get("status"), "summary": data.get("summary")}
        by_task.setdefault(gid, []).append(entry)

    for gid, rows in by_task.items():
        rows.sort(key=lambda r: ("-fix" in Path(r["path"]).stem, r["path"]))

    flat: list[dict] = []
    for rows in by_task.values():
        flat.extend(rows)
    return flat, by_task


def _load_completion_scores(*, task_gids: set[str] | None) -> list[float]:
    if not RETRO_DIR.is_dir():
        return []
    scores: list[float] = []
    for path in sorted(RETRO_DIR.glob("*-retro.json")):
        if path.name.endswith("-epic-retro.json"):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        gid = str(data.get("task_gid") or "")
        if task_gids is not None and gid and gid not in task_gids:
            continue
        score = data.get("completion_score")
        if isinstance(score, (int, float)) and 0 <= float(score) <= 100:
            scores.append(float(score))
    return scores


def compute_kpis(*, task_gids: set[str] | None) -> dict:
    verifications, by_task = _load_verification_reviews(task_gids=task_gids)
    scores = _load_completion_scores(task_gids=task_gids)

    verification_total = len(by_task)
    verification_passed = sum(
        1 for rows in by_task.values() if rows and rows[0].get("status") in PASSED
    )
    first_qa_pass_rate = (
        verification_passed / verification_total if verification_total else None
    )

    fix_rounds = sum(max(0, len(rows) - 1) for rows in by_task.values())
    fix_avg_rounds = fix_rounds / verification_total if verification_total else None

    completion_score_avg = sum(scores) / len(scores) if scores else None

    return {
        "schema_version": "1.0",
        "aggregated_at": datetime.now(timezone.utc).isoformat(),
        "verification_total": verification_total,
        "verification_passed": verification_passed,
        "first_qa_pass_rate": first_qa_pass_rate,
        "fix_avg_rounds": fix_avg_rounds,
        "retro_with_completion_score": len(scores),
        "completion_score_avg": completion_score_avg,
        "m6_targets": {
            "first_qa_pass_rate_min": 0.70,
            "fix_avg_rounds_max": 1.5,
            "must_ac_pass_rate_min": 1.0,
            "should_ac_pass_rate_min": 0.60,
        },
    }


def collect_subtask_gids(root_gid: str, token: str) -> set[str]:
    from asana_program_common import list_subtasks  # noqa: WPS433

    seen: set[str] = set()
    stack = [root_gid]
    while stack:
        gid = stack.pop()
        if not gid or gid in seen:
            continue
        seen.add(gid)
        for sub in list_subtasks(gid, token):
            sg = str(sub.get("gid") or "")
            if sg:
                stack.append(sg)
    return seen


def main() -> int:
    p = argparse.ArgumentParser(description="Aggregate delivery KPIs")
    p.add_argument("--parent", help="Epic GID: filter to subtree via Asana API")
    p.add_argument("--json", action="store_true", help="Print JSON to stdout")
    args = p.parse_args()

    task_gids: set[str] | None = None
    if args.parent:
        from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: WPS433

        load_env_from_dotfile()
        task_gids = collect_subtask_gids(args.parent, get_token())

    result = compute_kpis(task_gids=task_gids)
    if args.parent:
        result["parent_gid"] = args.parent

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        rate = result["first_qa_pass_rate"]
        rate_pct = f"{rate * 100:.1f}%" if rate is not None else "N/A"
        fix = result["fix_avg_rounds"]
        fix_s = f"{fix:.2f}" if fix is not None else "N/A"
        cs = result["completion_score_avg"]
        cs_s = f"{cs:.1f}" if cs is not None else "N/A"
        print(f"first_qa_pass_rate={rate_pct} fix_avg_rounds={fix_s} completion_score_avg={cs_s}")
        print(f"verification_total={result['verification_total']} retro_scores={result['retro_with_completion_score']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
