#!/usr/bin/env python3
"""Tests for create_retrospective_intake_tasks requester enforcement."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import create_retrospective_intake_tasks as crt  # noqa: E402


class RequesterNotesTests(unittest.TestCase):
    def test_placeholder_not_ok(self) -> None:
        self.assertFalse(crt.requester_notes_ok(crt.REQUESTER_PLACEHOLDER))

    def test_nonempty_ok(self) -> None:
        self.assertTrue(crt.requester_notes_ok("承認します"))

    @mock.patch("intake_from_asana.comments_markdown", return_value="承認コメント")
    @mock.patch("intake_from_asana.extract_requester_comments", return_value=[{"text": "ok"}])
    @mock.patch("asana_program_common.list_task_comment_stories", return_value=[])
    @mock.patch("asana_program_common.fetch_task", return_value={"assignee": {"gid": "1", "name": "Human"}})
    @mock.patch(
        "retrospective_intake_gate_util.find_retro_intake_gate_sub",
        return_value={"gid": "gate1", "completed": True},
    )
    def test_requester_notes_from_gate(
        self,
        _find: mock.MagicMock,
        _fetch: mock.MagicMock,
        _stories: mock.MagicMock,
        _extract: mock.MagicMock,
        _md: mock.MagicMock,
    ) -> None:
        notes = crt.requester_notes_from_gate("epic1", "token")
        self.assertEqual(notes, "承認コメント")

    @mock.patch(
        "retrospective_intake_gate_util.find_retro_intake_gate_sub",
        return_value=None,
    )
    def test_requester_notes_from_gate_missing(self, _find: mock.MagicMock) -> None:
        self.assertEqual(crt.requester_notes_from_gate("epic1", "token"), "")


if __name__ == "__main__":
    unittest.main()
