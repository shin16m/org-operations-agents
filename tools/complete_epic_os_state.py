#!/usr/bin/env python3
"""L1 hook: set org-os OS State=Done before Asana epic complete.

Non-blocking by default — warns and exits 0 if org-os CF is unset or transition fails.

Usage:
  python tools/complete_epic_os_state.py --epic <PARENT_GID>
  python tools/complete_epic_os_state.py --epic <PARENT_GID> --dry-run
  python tools/complete_epic_os_state.py --epic <PARENT_GID> --strict  # exit 1 on failure
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORG_OS = ROOT / "tools/org_os.py"
PY = ROOT / ".venv/Scripts/python.exe"
if not PY.is_file():
    PY = Path(sys.executable)


def main() -> int:
    p = argparse.ArgumentParser(description="Set org-os OS State=Done on epic (L1 workflow hook)")
    p.add_argument("--epic", required=True, help="Parent epic task GID")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--strict", action="store_true", help="Exit 1 if org-os complete fails")
    args = p.parse_args()

    cmd = [str(PY), str(ORG_OS), "complete", "--epic", args.epic]
    if args.dry_run:
        cmd.append("--dry-run")
    if not args.strict:
        cmd.append("--allow-skip")

    r = subprocess.run(cmd, cwd=str(ROOT))
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
