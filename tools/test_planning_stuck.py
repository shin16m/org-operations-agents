#!/usr/bin/env python3
"""Regression tests for planning-stuck detection / Done guard (asana_ops_poller)."""

from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
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


class CursorKickRoutingTests(unittest.TestCase):
    """_cursor_kick_hint must route by gate/phase (dry-run prints the cmd)."""

    def _hint_cmd(self, item: dict) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            poller._cursor_kick_hint(item, execute=False, dry_run=True, token=None)
        return buf.getvalue()

    def test_planning_approval_routes_to_execution_agent(self) -> None:
        # Post-approval RESUME must materialize execution children via the
        # workflow-orchestrator agent, not task_dispatcher (which has no target).
        out = self._hint_cmd(
            {"parent_gid": "EPIC", "phase": "execution", "gate_kind": "planning_approval"}
        )
        self.assertIn("cursor_epic_dispatch.py", out)
        self.assertIn("--mode execution", out)
        self.assertIn("--gate-kind planning_approval", out)
        self.assertNotIn("task_dispatcher.py", out)

    def test_plain_execution_routes_to_task_dispatcher(self) -> None:
        out = self._hint_cmd({"parent_gid": "EPIC", "phase": "execution", "gate_kind": "-"})
        self.assertIn("task_dispatcher.py", out)
        self.assertNotIn("cursor_epic_dispatch.py", out)

    def test_planning_phase_routes_to_planning_dispatch(self) -> None:
        out = self._hint_cmd(
            {"parent_gid": "EPIC", "phase": "planning", "planning_child_gid": "CHILD"}
        )
        self.assertIn("cursor_epic_dispatch.py", out)
        self.assertIn("--mode planning", out)


class ExecutionPromptKickTests(unittest.TestCase):
    def test_build_execution_prompt_includes_kick(self) -> None:
        from cursor_epic_dispatch import build_execution_prompt  # noqa: WPS433

        prompt = build_execution_prompt("1215436815983476", "planning_approval")
        self.assertIn("--kick -y", prompt)


if __name__ == "__main__":
    unittest.main()
