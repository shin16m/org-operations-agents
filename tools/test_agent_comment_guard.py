#!/usr/bin/env python3
"""Unit tests for agent_comment_guard."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

ASANA_OPT = Path(__file__).resolve().parents[1] / "skills/platform/asana-buddy/optional"
if str(ASANA_OPT) not in sys.path:
    sys.path.insert(0, str(ASANA_OPT))

import agent_comment_guard as guard  # noqa: E402


class ValidateCommentAgentTests(unittest.TestCase):
    def test_worker_must_match_assignee(self) -> None:
        task = {"notes": "チーム: development\n担当: requirements-writer\n", "parent": None}
        with mock.patch("asana_program_common.fetch_task", return_value=task):
            with mock.patch("asana_program_common.is_epic_task", return_value=False):
                err = guard.validate_comment_agent(
                    task_gid="SUB",
                    agent="product-manager",
                    skill="skills/development/product-manager/SKILL.md",
                    token="tok",
                )
        self.assertIsNotNone(err)
        self.assertIn("PM slug", err)

    def test_matching_worker_ok(self) -> None:
        task = {"notes": "チーム: development\n担当: developer\n", "parent": None}
        with mock.patch("asana_program_common.fetch_task", return_value=task):
            with mock.patch("asana_program_common.is_epic_task", return_value=False):
                err = guard.validate_comment_agent(
                    task_gid="SUB",
                    agent="developer",
                    skill="skills/development/developer/SKILL.md",
                    token="tok",
                )
        self.assertIsNone(err)


class ValidateWorkerCompleteTests(unittest.TestCase):
    def test_blocks_without_signed_comment(self) -> None:
        task = {
            "notes": "担当: developer\n",
            "name": "実装",
            "parent": {"gid": "PM"},
        }
        with mock.patch("asana_program_common.fetch_task", return_value=task):
            with mock.patch.object(guard, "has_agent_comment", return_value=False):
                err = guard.validate_worker_sub_complete(task_gid="SUB", token="tok")
        self.assertIsNotNone(err)
        self.assertIn("agent-work-record", err)

    def test_requirements_writer_needs_attach(self) -> None:
        task = {
            "notes": "担当: requirements-writer\nmode=requirements\n",
            "name": "要件定義",
            "parent": {"gid": "PM123"},
        }
        with mock.patch("asana_program_common.fetch_task", return_value=task):
            with mock.patch.object(guard, "has_agent_comment", return_value=True):
                with mock.patch.object(guard, "_attachment_names", return_value=set()):
                    err = guard.validate_worker_sub_complete(task_gid="SUB", token="tok")
        self.assertIsNotNone(err)
        self.assertIn("PM123-requirements.md", err)


if __name__ == "__main__":
    unittest.main()
