#!/usr/bin/env python3
"""Repo-root wrapper for products/org-os CLI (no pip install required).

Usage:
  python tools/run_org_os.py status --epic <GID>
  python tools/run_org_os.py dispatch --epic <GID> --dry-run
  python tools/run_org_os.py complete --epic <GID> [--allow-skip]
  python tools/run_org_os.py doctor
  python tools/run_org_os.py watch --project <GID> --once

Named run_org_os.py (not org_os.py) so tools/ on sys.path does not shadow the
org_os package when runner/poller import org_os.queue (C2 hotfix).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "products/org-os/src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from org_os.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
