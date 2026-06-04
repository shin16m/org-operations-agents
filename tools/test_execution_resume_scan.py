#!/usr/bin/env python3
"""Unit tests for execution_resume_scan state machine."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
ASANA_OPT = TOOLS.parent / "skills/platform/asana-buddy/optional"
for p in (str(TOOLS), str(ASANA_OPT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import execution_resume_scan as scan  # noqa: E402


class HasAgentCommentTests(unittest.TestCase):
    def test_detects_signature(self) -> None:
        stories = [
            {"text": "hello"},
            {"text": "---\n🤖 agent-work-record\nagent: dev-reviewer\n---"},
        ]
        with mock.patch.object(scan, "list_task_comment_stories", return_value=stories):
            self.assertTrue(scan.has_agent_comment("SUB", "dev-reviewer", "tok"))

    def test_rejects_other_agent(self) -> None:
        stories = [{"text": "agent-work-record\nagent: developer\n"}]
        with mock.patch.object(scan, "list_task_comment_stories", return_value=stories):
            self.assertFalse(scan.has_agent_comment("SUB", "dev-reviewer", "tok"))


class ClassifyPmChildTests(unittest.TestCase):
    def test_needs_pm_kick_when_no_workers(self) -> None:
        with mock.patch.object(scan, "_worker_subs", return_value=[]):
            with mock.patch.object(scan, "_find_review_sub", return_value=None):
                with mock.patch.object(scan, "fetch_task", return_value={"notes": "チーム: development"}):
                    out = scan.classify_pm_child(
                        epic_gid="EPIC",
                        pm_child={"gid": "PM", "name": "dev", "department": "development"},
                        token="tok",
                    )
        self.assertEqual(out["state"], "needs_pm_kick")

    def test_wait_pm_review(self) -> None:
        with mock.patch.object(scan, "_worker_subs", return_value=[{"gid": "W1", "assignee": "developer", "name": "x"}]):
            with mock.patch.object(
                scan, "_find_review_sub", return_value={"gid": "R1", "completed": False}
            ):
                with mock.patch.object(scan, "fetch_task", return_value={"notes": ""}):
                    out = scan.classify_pm_child(
                        epic_gid="EPIC",
                        pm_child={"gid": "PM", "name": "dev", "department": "development"},
                        token="tok",
                    )
        self.assertEqual(out["state"], "wait_pm_review")

    def test_needs_worker_kick(self) -> None:
        with mock.patch.object(
            scan,
            "_worker_subs",
            return_value=[{"gid": "W1", "assignee": "developer", "name": "impl"}],
        ):
            with mock.patch.object(scan, "_find_review_sub", return_value={"gid": "R1", "completed": True}):
                with mock.patch.object(scan, "has_agent_comment", return_value=False):
                    with mock.patch.object(scan, "fetch_task", return_value={"notes": ""}):
                        out = scan.classify_pm_child(
                            epic_gid="EPIC",
                            pm_child={"gid": "PM", "name": "dev", "department": "development"},
                            token="tok",
                        )
        self.assertEqual(out["state"], "needs_worker_kick")
        self.assertEqual(out["worker_sub_gid"], "W1")

    def test_needs_pm_complete(self) -> None:
        with mock.patch.object(
            scan,
            "_worker_subs",
            return_value=[{"gid": "W1", "assignee": "developer", "name": "impl"}],
        ):
            with mock.patch.object(scan, "_find_review_sub", return_value={"gid": "R1", "completed": True}):
                with mock.patch.object(scan, "has_agent_comment", return_value=True):
                    with mock.patch.object(scan, "fetch_task", return_value={"notes": ""}):
                        out = scan.classify_pm_child(
                            epic_gid="EPIC",
                            pm_child={"gid": "PM", "name": "dev", "department": "development"},
                            token="tok",
                        )
        self.assertEqual(out["state"], "needs_pm_complete")


class KickCmdTests(unittest.TestCase):
    def test_worker_kick_cmd(self) -> None:
        cmd = scan._kick_cmd_for_action(
            {
                "state": "needs_worker_kick",
                "epic_gid": "E1",
                "pm_child_gid": "PM1",
                "department": "development",
            }
        )
        self.assertIsNotNone(cmd)
        assert cmd is not None
        self.assertIn("cursor_worker_dispatch.py", " ".join(cmd))

    def test_pm_complete_cmd(self) -> None:
        cmd = scan._kick_cmd_for_action(
            {
                "state": "needs_pm_complete",
                "epic_gid": "E1",
                "pm_child_gid": "PM1",
                "worker_sub_gid": "W1",
                "department": "development",
            }
        )
        self.assertIsNotNone(cmd)
        assert cmd is not None
        self.assertIn("pm_worker_complete_bridge.py", " ".join(cmd))


class ExecutionPromptTests(unittest.TestCase):
    def test_execution_prompt_includes_kick(self) -> None:
        from cursor_epic_dispatch import build_execution_prompt  # noqa: WPS433

        prompt = build_execution_prompt("EPIC", "planning_approval")
        self.assertIn("task_dispatcher.py", prompt)
        self.assertIn("--kick -y", prompt)


if __name__ == "__main__":
    unittest.main()
