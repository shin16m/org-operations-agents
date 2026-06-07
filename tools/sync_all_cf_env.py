#!/usr/bin/env python3
"""Sync all org-ops CF GIDs (org-os · task type · assignee type) in one command.

Usage:
  python tools/sync_all_cf_env.py --project <GID> --dry-run
  python tools/sync_all_cf_env.py --project <GID> --write -y
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNC_SCRIPTS = (
    "sync_org_os_cf_env.py",
    "sync_task_type_env.py",
    "sync_assignee_type_env.py",
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", required=True, help="Asana project GID")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--write", action="store_true")
    p.add_argument("-y", action="store_true")
    p.add_argument("--env-file", type=Path, default=None)
    args = p.parse_args()

    if not args.dry_run and not args.write:
        p.error("use --dry-run or --write")

    py = sys.executable
    mode_flag = "--dry-run" if args.dry_run else "--write"
    extra = ["-y"] if args.write and args.y else []

    print(f"SYNC_ALL  project={args.project}  mode={mode_flag}")
    for script in SYNC_SCRIPTS:
        cmd = [py, str(ROOT / "tools" / script), "--project", args.project, mode_flag, *extra]
        if args.env_file:
            cmd.extend(["--env-file", str(args.env_file)])
        print(f"RUN  {' '.join(cmd)}")
        rc = subprocess.call(cmd, cwd=ROOT)
        if rc != 0:
            print(f"FAIL  {script} exit {rc}", file=sys.stderr)
            return rc

    print("PASS  all CF sync scripts completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
