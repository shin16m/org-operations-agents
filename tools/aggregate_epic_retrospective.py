#!/usr/bin/env python3
"""Aggregate per-task retro JSON files into epic-retro.json (R3).

Usage:
  python tools/aggregate_epic_retrospective.py --parent <EPIC_GID>
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/platform/retrospectives"


def main() -> int:
    p = argparse.ArgumentParser(description="Aggregate epic retrospective")
    p.add_argument("--parent", required=True, help="Epic parent GID")
    args = p.parse_args()

    task_retros: list[dict] = []
    seen: set[str] = set()
    for path in sorted(OUT.glob("*-retro.json")):
        if path.name.endswith("-epic-retro.json"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        tg = str(data.get("task_gid") or "")
        if not tg or tg in seen:
            continue
        seen.add(tg)
        task_retros.append(data)

    candidates: list[dict] = []
    for tr in task_retros:
        for i, text in enumerate(tr.get("intake_candidates") or [], 1):
            candidates.append(
                {
                    "id": f"{tr.get('task_gid')}-{i}",
                    "source_task_gid": tr.get("task_gid"),
                    "source_agent": tr.get("agent"),
                    "summary": text,
                }
            )

    epic = {
        "schema_version": "1.0",
        "parent_gid": args.parent,
        "aggregated_at": datetime.now(timezone.utc).isoformat(),
        "task_retrospectives": task_retros,
        "intake_candidates": candidates,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    out_path = OUT / f"{args.parent}-epic-retro.json"
    out_path.write_text(json.dumps(epic, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out_path, f"tasks={len(task_retros)} candidates={len(candidates)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
