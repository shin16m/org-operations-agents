#!/usr/bin/env python3
"""Tests for emit_milestone_effectiveness_report."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import emit_milestone_effectiveness_report as emit  # noqa: E402

PY = ROOT / ".venv/Scripts/python.exe"
if not PY.is_file():
    PY = Path(sys.executable)


class TestRenderMd(unittest.TestCase):
    def test_render_includes_score(self) -> None:
        md = emit._render_md({"title": "T", "milestone_id": "t", "score": 75, "status": "warn"})
        self.assertIn("75", md)
        self.assertIn("warn", md)


class TestCli(unittest.TestCase):
    def test_help(self) -> None:
        r = subprocess.run(
            [str(PY), str(TOOLS / "emit_milestone_effectiveness_report.py"), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(r.returncode, 0)

if __name__ == "__main__":
    unittest.main()
