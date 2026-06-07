#!/usr/bin/env python3
"""Unit tests for win_subprocess."""

from __future__ import annotations

import subprocess
import sys
import unittest
from unittest import mock

TOOLS = __import__("pathlib").Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import win_subprocess as ws  # noqa: E402


class WinSubprocessTests(unittest.TestCase):
    def test_no_window_flags_zero_on_linux(self) -> None:
        with mock.patch.object(ws.sys, "platform", "linux"):
            self.assertEqual(ws.creationflags_no_window(), 0)
            self.assertEqual(ws.creationflags_isolated_worker(), 0)

    def test_no_window_flags_on_win32(self) -> None:
        with mock.patch.object(ws.sys, "platform", "win32"):
            with mock.patch.object(subprocess, "CREATE_NO_WINDOW", 134217728, create=True):
                self.assertEqual(ws.creationflags_no_window(), 134217728)

    def test_run_injects_creationflags_on_win32(self) -> None:
        with mock.patch.object(ws.sys, "platform", "win32"):
            with mock.patch.object(subprocess, "CREATE_NO_WINDOW", 8, create=True):
                with mock.patch.object(ws.subprocess, "run") as mock_run:
                    mock_run.return_value = subprocess.CompletedProcess([], 0)
                    ws.run(["echo"], cwd=".")
                    mock_run.assert_called_once()
                    _, kwargs = mock_run.call_args
                    self.assertEqual(kwargs.get("creationflags"), 8)

    def test_run_preserves_explicit_creationflags(self) -> None:
        with mock.patch.object(ws.sys, "platform", "win32"):
            with mock.patch.object(ws.subprocess, "run") as mock_run:
                mock_run.return_value = subprocess.CompletedProcess([], 0)
                ws.run(["echo"], creationflags=99)
                _, kwargs = mock_run.call_args
                self.assertEqual(kwargs.get("creationflags"), 99)

    def test_win_bridge_argv_none_on_linux(self) -> None:
        with mock.patch.object(ws.sys, "platform", "linux"):
            self.assertIsNone(ws.win_bridge_command_argv())


if __name__ == "__main__":
    unittest.main()
