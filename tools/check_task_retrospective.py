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


def _valid_completion_score(value: object) -> bool:
    if not isinstance(value, (int, float)):
        return False
    return 0 <= float(value) <= 100


def check_retrospective(task_gid: str, *, require_completion_score: bool) -> int:
    path = OUT / f"{task_gid}-retro.json"
    if not path.is_file():
        print(f"missing retrospective: {path}", file=sys.stderr)
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    if require_completion_score:
        score = data.get("completion_score")
        if score is None:
            print(
                f"missing completion_score in {path} (Must AC pass rate 0-100 required)",
                file=sys.stderr,
            )
            return 1
        if not _valid_completion_score(score):
            print(
                f"invalid completion_score in {path}: {score!r} (expected 0-100)",
                file=sys.stderr,
            )
            return 1

    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Check task retrospective JSON")
    p.add_argument("--task", required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--no-require-completion-score",
        action="store_true",
        help="Legacy: do not require completion_score field",
    )
    args = p.parse_args()

    path = OUT / f"{args.task}-retro.json"
    if not path.is_file():
        if args.json:
            print(json.dumps({"status": "missing", "path": str(path)}))
        else:
            print(f"missing retrospective: {path}", file=sys.stderr)
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    rc = check_retrospective(
        args.task,
        require_completion_score=not args.no_require_completion_score,
    )
    if rc != 0:
        if args.json:
            print(json.dumps({"status": "invalid", "path": str(path)}))
        return rc

    if args.json:
        print(
            json.dumps(
                {
                    "status": "ok",
                    "path": str(path),
                    "agent": data.get("agent"),
                    "completion_score": data.get("completion_score"),
                }
            )
        )
    else:
        print(f"OK {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
