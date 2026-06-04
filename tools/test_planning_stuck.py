#!/usr/bin/env python3
"""Regression tests for planning-stuck detection / Done guard (asana_ops_poller)."""

from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
ASANA_OPT = TOOLS.parent / "skills/platform/asana-buddy/optional"
for p in (str(TOOLS), str(ASANA_OPT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import asana_ops_poller as poller  # noqa: E402


class PlanningStuckTests(unittest.TestCase):
    def _run(self, find_subtask_return) -> str:
        buf = io.StringIO()
        with mock.patch("check_approval_subtask._find_subtask", return_value=find_subtask_return):
            with redirect_stderr(buf):
                poller._warn_planning_stuck_without_approval("EPIC", "CHILD", "tok")
        return buf.getvalue()

    def test_warns_when_no_approval_sub(self) -> None:
        out = self._run(None)
        self.assertIn("planning_stuck", out)
        self.assertIn("no_open_approval_sub", out)

    def test_silent_when_open_approval_exists(self) -> None:
        out = self._run({"gid": "1", "completed": False})
        self.assertEqual(out, "")

    def test_silent_when_approval_completed(self) -> None:
        # Completed approval = gate passed → not stuck (Done guard not triggered here).
        out = self._run({"gid": "1", "completed": True})
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
