#!/usr/bin/env python3
"""Tests for execution kick guard (intake 1215465107786667)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
ASANA_OPT = TOOLS.parent / "skills/platform/asana-buddy/optional"
ORG_OS = TOOLS.parent / "products/org-os/src"
for p in (str(TOOLS), str(ASANA_OPT), str(ORG_OS)):
    if p not in sys.path:
        sys.path.insert(0, p)

import execution_kick_guard as guard  # noqa: E402


class ExecutionKickGuardTests(unittest.TestCase):
    def test_blocks_when_not_running(self) -> None:
        with mock.patch("org_os.asana_client.fetch_task", return_value={}):
            with mock.patch("org_os.asana_client.read_os_state", return_value="Waiting"):
                ok, reason = guard.execution_kick_allowed("EPIC", "tok")
        self.assertFalse(ok)
        self.assertIn("Waiting", reason)

    def test_blocks_when_ready(self) -> None:
        with mock.patch("org_os.asana_client.fetch_task", return_value={}):
            with mock.patch("org_os.asana_client.read_os_state", return_value="Ready"):
                ok, reason = guard.execution_kick_allowed("EPIC", "tok")
        self.assertFalse(ok)
        self.assertIn("Ready", reason)

    def test_blocks_when_planning_open(self) -> None:
        subs = [{"gid": "PLAN", "name": "【1/3・企画】", "completed": False}]

        def _fetch(gid: str, tok: str) -> dict:
            return {"notes": "チーム: planning\n担当: planning-pm"}

        with mock.patch("org_os.asana_client.fetch_task", return_value={}):
            with mock.patch("org_os.asana_client.read_os_state", return_value="Running"):
                with mock.patch("asana_program_common.fetch_task", side_effect=_fetch):
                    with mock.patch("asana_program_common.list_subtasks", return_value=subs):
                        with mock.patch(
                            "dispatch_prompt_util.infer_department",
                            return_value="planning",
                        ):
                            ok, reason = guard.execution_kick_allowed("EPIC", "tok")
        self.assertFalse(ok)
        self.assertIn("planning_child_open", reason)

    def test_allows_when_running_and_planning_done(self) -> None:
        with mock.patch("org_os.asana_client.fetch_task", return_value={}):
            with mock.patch("org_os.asana_client.read_os_state", return_value="Running"):
                with mock.patch("asana_program_common.list_subtasks", return_value=[]):
                    ok, reason = guard.execution_kick_allowed("EPIC", "tok")
        self.assertTrue(ok)
        self.assertEqual(reason, "ok")

    def test_log_blocked_format(self) -> None:
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            guard.log_blocked(epic_gid="EPIC", tool="test_tool", reason="epic_state=Waiting")
        out = buf.getvalue()
        self.assertIn("BLOCKED", out)
        self.assertIn("EPIC", out)
        self.assertIn("Waiting", out)


if __name__ == "__main__":
    unittest.main()
