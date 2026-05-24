#!/usr/bin/env python3
"""Save per-task retrospective JSON (R2).

Usage:
  python tools/record_task_retrospective.py --task <GID> --agent ssot-implementer \\
    --went-well "..." --improve "..." --intake-candidate "..."
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
    p = argparse.ArgumentParser(description="Record task retrospective JSON")
    p.add_argument("--task", required=True)
    p.add_argument("--agent", required=True)
    p.add_argument("--went-well", action="append", default=[])
    p.add_argument("--improve", action="append", default=[])
    p.add_argument("--intake-candidate", action="append", default=[])
    p.add_argument("--notes", default="")
    args = p.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{args.task}-retro.json"
    data = {
        "schema_version": "1.0",
        "task_gid": args.task,
        "agent": args.agent,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "went_well": list(args.went_well or []),
        "improve": list(args.improve or []),
        "intake_candidates": list(args.intake_candidate or []),
        "notes": (args.notes or "").strip(),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
