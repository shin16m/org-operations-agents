#!/usr/bin/env python3
"""Check task retrospective exists (JSON file).

Exit 0 if output/platform/retrospectives/<task>-retro.json exists.
Exit 1 if missing.

Usage:
  python tools/check_task_retrospective.py --task <GID>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/platform/retrospectives"


def main() -> int:
    p = argparse.ArgumentParser(description="Check task retrospective JSON")
    p.add_argument("--task", required=True)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    path = OUT / f"{args.task}-retro.json"
    if not path.is_file():
        if args.json:
            print(json.dumps({"status": "missing", "path": str(path)}))
        else:
            print(f"missing retrospective: {path}", file=sys.stderr)
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    if args.json:
        print(json.dumps({"status": "ok", "path": str(path), "agent": data.get("agent")}))
    else:
        print(f"OK {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
