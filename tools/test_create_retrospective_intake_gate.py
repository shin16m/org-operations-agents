#!/usr/bin/env python3
"""Tests for create_retrospective_intake_gate — notes generation and CLI wiring."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import create_retrospective_intake_gate as crig  # noqa: E402
from retrospective_intake_gate_util import GATE_TITLE  # noqa: E402


class NotesFromRetroTests(unittest.TestCase):
    def test_notes_lists_candidates(self) -> None:
        retro = Path(self._tmpdir()) / "epic-retro.json"
        retro.write_text(
            json.dumps(
                {
                    "parent_gid": "111",
                    "intake_candidates": [
                        {
                            "summary": "Improve assign plan",
                            "source_task_gid": "222",
                            "source_agent": "developer",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        notes = crig._notes_from_retro(retro)
        self.assertIn("Improve assign plan", notes)
        self.assertIn("222", notes)
        self.assertIn("create_retrospective_intake_tasks.py", notes)

    def test_notes_empty_candidates(self) -> None:
        retro = Path(self._tmpdir()) / "empty-retro.json"
        retro.write_text(json.dumps({"parent_gid": "111", "intake_candidates": []}), encoding="utf-8")
        notes = crig._notes_from_retro(retro)
        self.assertIn("候補なし", notes)

    def _tmpdir(self) -> str:
        import tempfile

        return tempfile.mkdtemp()


class MainOptOutTests(unittest.TestCase):
    @mock.patch("create_retrospective_intake_gate.subprocess.check_call")
    @mock.patch("create_retrospective_intake_gate.human_retro_intake_gate_requested", return_value=False)
    @mock.patch("create_retrospective_intake_gate.get_token")
    @mock.patch("create_retrospective_intake_gate.load_env_from_dotfile")
    def test_skip_gate_does_not_call_subprocess(
        self,
        _load: mock.MagicMock,
        _token: mock.MagicMock,
        _requested: mock.MagicMock,
        check_call: mock.MagicMock,
    ) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            retro = Path(tmp) / "retro.json"
            retro.write_text(json.dumps({"parent_gid": "999", "intake_candidates": []}), encoding="utf-8")
            with mock.patch(
                "sys.argv",
                [
                    "create_retrospective_intake_gate.py",
                    "--parent",
                    "999",
                    "--retro",
                    str(retro),
                    "--skip-gate",
                    "-y",
                ],
            ):
                crig.main()
        check_call.assert_not_called()

    @mock.patch("create_retrospective_intake_gate.subprocess.check_call")
    @mock.patch("create_retrospective_intake_gate.human_retro_intake_gate_requested", return_value=True)
    @mock.patch("create_retrospective_intake_gate.get_token")
    @mock.patch("create_retrospective_intake_gate.load_env_from_dotfile")
    def test_gate_requested_invokes_approval_subtask(
        self,
        _load: mock.MagicMock,
        _token: mock.MagicMock,
        _requested: mock.MagicMock,
        check_call: mock.MagicMock,
    ) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            retro = Path(tmp) / "retro.json"
            retro.write_text(json.dumps({"parent_gid": "999", "intake_candidates": []}), encoding="utf-8")
            with mock.patch(
                "sys.argv",
                [
                    "create_retrospective_intake_gate.py",
                    "--parent",
                    "999",
                    "--retro",
                    str(retro),
                    "-y",
                ],
            ):
                crig.main()
        check_call.assert_called_once()
        cmd = check_call.call_args[0][0]
        self.assertIn("create_approval_subtask.py", cmd[1])
        self.assertIn(GATE_TITLE, cmd)
        self.assertIn("-y", cmd)


if __name__ == "__main__":
    unittest.main()
