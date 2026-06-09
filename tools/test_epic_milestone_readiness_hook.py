#!/usr/bin/env python3
"""Tests for milestone readiness complete hook."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import epic_milestone_readiness_hook as hook  # noqa: E402


class TestMilestoneTrackerDetection(unittest.TestCase):
    def test_is_milestone_tracker_by_title(self) -> None:
        self.assertTrue(hook.is_milestone_tracker("[M5] 学習ループ — マイルストーン", ""))

    def test_is_milestone_tracker_by_notes(self) -> None:
        self.assertTrue(hook.is_milestone_tracker("x", "milestone_tracker: true"))

    def test_not_tracker(self) -> None:
        self.assertFalse(hook.is_milestone_tracker("普通の governance 子", ""))

    def test_resolve_checklist_m5(self) -> None:
        path = hook.resolve_checklist("[M5] 学習ループ閉鎖 — マイルストーン", "")
        self.assertIn("m5-learning-loop.json", path or "")


class TestHookBehavior(unittest.TestCase):
    def test_skip_non_tracker(self) -> None:
        with mock.patch.object(hook, "_fetch_task_text", return_value=("普通", "")):
            ev = hook.evaluate_task("123")
        self.assertEqual(ev.kind, "skip")

    def test_ok_when_check_passes(self) -> None:
        with mock.patch.object(
            hook, "_fetch_task_text", return_value=("[M5] x — マイルストーン", "")
        ), mock.patch.object(
            hook, "run_readiness_check", return_value=(0, "MILESTONE_READINESS score=85.0 status=achieved")
        ):
            ev = hook.evaluate_task("1215475369302645")
        self.assertEqual(ev.kind, "ok")
        self.assertEqual(ev.score, 85.0)


if __name__ == "__main__":
    unittest.main()
