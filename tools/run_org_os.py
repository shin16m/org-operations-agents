#!/usr/bin/env python3
"""Repo-root wrapper for products/org-os CLI — DEPRECATED (2026-06-09).

org-os は本番運用から除外。履歴・開発参照のみ。
SSOT: docs/design/chat-driven-ops.md · products/_retired/README.md

Usage (non-production):
  python tools/run_org_os.py doctor
  python tools/run_org_os.py status --epic <GID>

Named run_org_os.py (not org_os.py) so tools/ on sys.path does not shadow org_os.
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
