#!/usr/bin/env python3
"""Regression tests for complete_task epic detection / org-os hook."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

ASANA_OPT = Path(__file__).resolve().parents[1] / "skills/platform/asana-buddy/optional"
if str(ASANA_OPT) not in sys.path:
    sys.path.insert(0, str(ASANA_OPT))

from asana_program_common import is_epic_task  # noqa: E402


class IsEpicTaskTests(unittest.TestCase):
    def test_task_type_epic(self) -> None:
        with mock.patch("asana_program_common.read_task_type", return_value="Epic"):
            self.assertTrue(is_epic_task("1", "tok"))

    def test_heuristic_parentless_with_children(self) -> None:
        with mock.patch("asana_program_common.read_task_type", return_value=None):
            with mock.patch(
                "asana_program_common.fetch_task",
                return_value={"gid": "1", "parent": None},
            ):
                with mock.patch(
                    "asana_program_common.list_subtasks",
                    return_value=[{"gid": "2"}],
                ):
                    self.assertTrue(is_epic_task("1", "tok"))

    def test_not_epic_when_parent_exists(self) -> None:
        with mock.patch("asana_program_common.read_task_type", return_value=None):
            with mock.patch(
                "asana_program_common.fetch_task",
                return_value={"gid": "1", "parent": {"gid": "P"}},
            ):
                self.assertFalse(is_epic_task("1", "tok"))

    def test_not_epic_parentless_no_children(self) -> None:
        with mock.patch("asana_program_common.read_task_type", return_value=None):
            with mock.patch(
                "asana_program_common.fetch_task",
                return_value={"gid": "1", "parent": None},
            ):
                with mock.patch("asana_program_common.list_subtasks", return_value=[]):
                    self.assertFalse(is_epic_task("1", "tok"))

    def test_intake_not_epic_without_children_heuristic(self) -> None:
        with mock.patch("asana_program_common.read_task_type", return_value="Intake"):
            with mock.patch(
                "asana_program_common.fetch_task",
                return_value={"gid": "1", "parent": None},
            ):
                with mock.patch("asana_program_common.list_subtasks", return_value=[]):
                    self.assertFalse(is_epic_task("1", "tok"))


class CompleteTaskHookTests(unittest.TestCase):
    def test_org_os_called_before_complete(self) -> None:
        import complete_task as mod  # noqa: E402

        argv = ["complete_task.py", "--gid", "1", "-y"]
        with mock.patch("sys.argv", argv):
            with mock.patch.object(mod, "load_env_from_dotfile"):
                with mock.patch.object(mod, "get_token", return_value="tok"):
                    with mock.patch.object(mod, "fetch_task", return_value={"name": "epic"}):
                        with mock.patch.object(mod, "is_human_gate_task_name", return_value=False):
                            with mock.patch.object(mod, "is_epic_task", return_value=True):
                                with mock.patch.object(
                                    mod, "_org_os_complete_epic", return_value=0
                                ) as org_os:
                                    with mock.patch.object(
                                        mod,
                                        "set_task_completed",
                                        return_value={"gid": "1", "completed": True},
                                    ):
                                        mod.main()
        org_os.assert_called_once_with("1", dry_run=False, strict=False)


if __name__ == "__main__":
    unittest.main()
