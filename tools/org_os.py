#!/usr/bin/env python3
"""Repo-root wrapper for products/org-os CLI (no pip install required).

Usage:
  python tools/org_os.py status --epic <GID>
  python tools/org_os.py dispatch --epic <GID> --dry-run
  python tools/org_os.py complete --epic <GID> [--allow-skip]
  python tools/org_os.py watch --project <GID> --once
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
