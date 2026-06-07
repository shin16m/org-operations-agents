#!/usr/bin/env python3
"""Tests for assign plan [retro] auto-inclusion in pm_assign_subtasks."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

OPTIONAL = Path(__file__).resolve().parents[1] / "skills/platform/asana-buddy/optional"
if str(OPTIONAL) not in sys.path:
    sys.path.insert(0, str(OPTIONAL))

import create_retro_subtask as retro  # noqa: E402
import pm_assign_subtasks as pas  # noqa: E402


class PlanRetroFlagTests(unittest.TestCase):
    def test_item_level_retro(self) -> None:
        plan = {"include_retro_subtasks": False}
        item = {"retro": True}
        self.assertTrue(pas.plan_includes_retro(plan, item))

    def test_plan_level_retro(self) -> None:
        plan = {"include_retro_subtasks": True}
        item = {}
        self.assertTrue(pas.plan_includes_retro(plan, item))

    def test_default_off(self) -> None:
        self.assertFalse(pas.plan_includes_retro({}, {}))


class RetroHelperTests(unittest.TestCase):
    def test_title_format(self) -> None:
        self.assertEqual(
            retro.retro_subtask_title("developer"),
            "[retro] developer — 所感・改善案",
        )

    @mock.patch("create_retro_subtask.create_subtask")
    @mock.patch("create_retro_subtask.list_subtasks", return_value=[])
    def test_ensure_creates_nested(self, _list: mock.Mock, create: mock.Mock) -> None:
        create.return_value = {"gid": "R1"}
        status, gid = retro.ensure_retro_subtask(
            "W1",
            "developer",
            department="development",
            token="tok",
        )
        self.assertEqual(status, "created")
        self.assertEqual(gid, "R1")
        create.assert_called_once()
        args = create.call_args[0]
        self.assertEqual(args[0], "W1")
        self.assertIn("[retro] developer", args[1])

    @mock.patch("create_retro_subtask.create_subtask")
    @mock.patch(
        "create_retro_subtask.list_subtasks",
        return_value=[{"gid": "R0", "name": "[retro] developer — 所感・改善案", "completed": False}],
    )
    def test_ensure_idempotent(self, _list: mock.Mock, create: mock.Mock) -> None:
        status, gid = retro.ensure_retro_subtask(
            "W1",
            "developer",
            department="development",
            token="tok",
        )
        self.assertEqual(status, "exists_open")
        self.assertEqual(gid, "R0")
        create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
