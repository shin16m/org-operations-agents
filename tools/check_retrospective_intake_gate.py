#!/usr/bin/env python3
"""Check epic retrospective intake approval gate.

Usage:
  python tools/check_retrospective_intake_gate.py --parent <EPIC_GID>
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPTIONAL = ROOT / "skills/platform/asana-buddy/optional"
MARKER = "【承認】レトロ改善候補"


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Check retrospective intake gate")
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
