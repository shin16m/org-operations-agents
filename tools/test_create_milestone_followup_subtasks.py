#!/usr/bin/env python3
"""Tests for create_milestone_followup_subtasks."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import create_milestone_followup_subtasks as followup  # noqa: E402

PY = ROOT / ".venv/Scripts/python.exe"
if not PY.is_file():
    PY = Path(sys.executable)


class TestFollowup(unittest.TestCase):
    def test_skip_high_score(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({"score": 90, "gaps": [], "follow_up_candidates": []}, f)
            path = f.name
        try:
            sys.argv = [
                "create_milestone_followup_subtasks.py",
                "--report",
                path,
                "--parent",
                "123",
            ]
            self.assertEqual(followup.main(), 0)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_dry_run_candidates(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(
                {
                    "score": 55,
                    "gaps": [{"check_id": "x", "message": "fail", "severity": "P0"}],
                    "follow_up_candidates": [],
                },
                f,
            )
            path = f.name
        try:
            sys.argv = [
                "create_milestone_followup_subtasks.py",
                "--report",
                path,
                "--parent",
                "123",
            ]
            self.assertEqual(followup.main(), 0)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_cli_help(self) -> None:
        r = subprocess.run(
            [str(PY), str(TOOLS / "create_milestone_followup_subtasks.py"), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
