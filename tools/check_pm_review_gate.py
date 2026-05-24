#!/usr/bin/env python3
"""Check PM assign-review gate subtask completion.

Usage:
  python tools/check_pm_review_gate.py --parent <PM子GID>
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPTIONAL = ROOT / "skills/platform/asana-buddy/optional"
MARKER = "【レビュー】"


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Check PM assign-review gate")
    p.add_argument("--parent", required=True)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    cmd = [
        sys.executable,
        str(OPTIONAL / "check_approval_subtask.py"),
        "--parent",
        args.parent,
        "--marker",
        MARKER,
    ]
    if args.json:
        cmd.append("--json")
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    sys.exit(main())
