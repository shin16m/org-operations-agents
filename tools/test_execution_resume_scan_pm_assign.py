#!/usr/bin/env python3
"""Tests for execution_resume_scan development pm_assign hint."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import execution_resume_scan as scan  # noqa: E402


class PmAssignHintTests(unittest.TestCase):
    @mock.patch("execution_resume_scan._worker_subs", return_value=[])
    @mock.patch("execution_resume_scan._find_review_sub", return_value=None)
    @mock.patch("execution_resume_scan.fetch_task", return_value={"notes": "チーム: development"})
    @mock.patch("execution_resume_scan.infer_department", return_value="development")
    def test_development_needs_pm_assign_hint(
        self,
        _infer: mock.Mock,
        _fetch: mock.Mock,
        _review: mock.Mock,
        _workers: mock.Mock,
    ) -> None:
        out = scan.classify_pm_child(
            epic_gid="EPIC",
            pm_child={"gid": "PM1", "name": "dev child"},
            token="tok",
        )
        self.assertEqual(out["state"], "needs_pm_kick")
        self.assertEqual(out["reason"], "pm_assign_lite_required")
        self.assertIn("pm_assign_subtasks.py", out.get("pm_assign_hint", ""))


if __name__ == "__main__":
    unittest.main()
