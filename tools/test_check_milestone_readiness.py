#!/usr/bin/env python3
"""Tests for milestone readiness evaluator."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import check_milestone_readiness as cmr  # noqa: E402

M5_CHECKLIST = ROOT / "docs/verification/fixtures/milestone-readiness/m5-learning-loop.json"
PY = ROOT / ".venv/Scripts/python.exe"
if not PY.is_file():
    PY = Path(sys.executable)


class TestMilestoneReadinessHelpers(unittest.TestCase):
    def test_status_for_score(self) -> None:
        self.assertEqual(cmr._status_for_score(85, 80, 70), "achieved")
        self.assertEqual(cmr._status_for_score(75, 80, 70), "warn")
        self.assertEqual(cmr._status_for_score(60, 80, 70), "not_achieved")

    def test_axis_scores(self) -> None:
        checks = [
            {"axis": "parts", "weight": 10, "result": "pass"},
            {"axis": "parts", "weight": 10, "result": "fail"},
            {"axis": "enforcement", "weight": 20, "result": "pass"},
        ]
        axes = cmr._axis_scores(checks)
        self.assertEqual(axes["parts"], 50.0)
        self.assertEqual(axes["enforcement"], 100.0)
        self.assertEqual(axes["e2e"], 0.0)

    def test_file_exists_check(self) -> None:
        ok, _ = cmr._check_file_exists("docs/design/milestone-effectiveness-standard.md")
        self.assertTrue(ok)
        ok2, _ = cmr._check_file_exists("docs/design/no-such-file-xyz.md")
        self.assertFalse(ok2)


class TestEvaluateChecklist(unittest.TestCase):
    def test_evaluate_produces_report(self) -> None:
        data = json.loads(M5_CHECKLIST.read_text(encoding="utf-8"))
        with mock.patch.object(cmr, "run_check", return_value=("pass", "ok")):
            report = cmr.evaluate_checklist(
                data,
                checklist_path="docs/verification/fixtures/milestone-readiness/m5-learning-loop.json",
            )
        self.assertEqual(report["score"], 100.0)
        self.assertEqual(report["status"], "achieved")
        self.assertEqual(report["milestone_id"], "m5-learning-loop")

    def test_evaluate_records_gaps_on_fail(self) -> None:
        data = {
            "schema_version": "1.0",
            "milestone_id": "t",
            "title": "T",
            "min_score_achieved": 80,
            "min_score_warn": 70,
            "checks": [
                {
                    "id": "x",
                    "description": "fail me",
                    "check_type": "file_exists",
                    "target": "missing.json",
                    "weight": 100,
                    "axis": "parts",
                    "severity_on_fail": "P0",
                }
            ],
        }
        report = cmr.evaluate_checklist(data, checklist_path="t.json")
        self.assertEqual(report["status"], "not_achieved")
        self.assertEqual(len(report["gaps"]), 1)
        self.assertEqual(report["gaps"][0]["severity"], "P0")


class TestCliIntegration(unittest.TestCase):
    def test_cli_help(self) -> None:
        r = subprocess.run(
            [str(PY), str(TOOLS / "check_milestone_readiness.py"), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("--checklist", r.stdout)

    def test_m5_checklist_runs(self) -> None:
        r = subprocess.run(
            [
                str(PY),
                str(TOOLS / "check_milestone_readiness.py"),
                "--checklist",
                str(M5_CHECKLIST),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertIn("MILESTONE_READINESS", r.stderr)
        self.assertIn("milestone_id", r.stdout)
        payload = json.loads(r.stdout)
        self.assertIn(payload["status"], ("achieved", "warn", "not_achieved"))
        self.assertGreaterEqual(payload["score"], 0)


if __name__ == "__main__":
    unittest.main()
