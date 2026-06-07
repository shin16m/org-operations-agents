#!/usr/bin/env python3
"""Unit tests for execution_resume_scan state machine."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
ASANA_OPT = TOOLS.parent / "skills/platform/asana-buddy/optional"
for p in (str(TOOLS), str(ASANA_OPT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import agent_comment_guard as guard  # noqa: E402
import execution_resume_scan as scan  # noqa: E402


class HasAgentCommentTests(unittest.TestCase):
    def test_detects_signature(self) -> None:
        stories = [
            {"text": "hello"},
            {"text": "---\n🤖 agent-work-record\nagent: dev-reviewer\n---"},
        ]
        with mock.patch(
            "asana_program_common.list_task_comment_stories",
            return_value=stories,
        ):
            self.assertTrue(guard.has_agent_comment("SUB", "dev-reviewer", "tok"))

    def test_rejects_other_agent(self) -> None:
        stories = [{"text": "agent-work-record\nagent: developer\n"}]
        with mock.patch(
            "asana_program_common.list_task_comment_stories",
            return_value=stories,
        ):
            self.assertFalse(guard.has_agent_comment("SUB", "dev-reviewer", "tok"))


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


class ScanExecutionKickChainTests(unittest.TestCase):
    def test_chains_kicks_with_rescan(self) -> None:
        kick_worker = {
            "epic_gid": "E1",
            "state": "needs_worker_kick",
            "pm_child_gid": "PM",
            "worker_sub_gid": "W1",
            "reason": "incomplete_worker_without_comment",
        }
        kick_complete = {
            "epic_gid": "E1",
            "state": "needs_pm_complete",
            "pm_child_gid": "PM",
            "worker_sub_gid": "W1",
            "department": "development",
            "reason": "worker_comment_without_complete",
        }
        idle = {"epic_gid": "E1", "state": "idle", "pm_child_gid": "PM"}
        main_scans = [[kick_worker], [kick_complete], [idle]]
        rescan_scans = [[kick_complete], [idle]]
        main_idx = 0
        rescan_idx = 0

        def _fake_collect(
            _projects,
            *,
            token,
            dry_run,
            log_scan=True,
            tick_stuck=True,
        ):  # noqa: ANN001
            nonlocal main_idx, rescan_idx
            if log_scan:
                idx = min(main_idx, len(main_scans) - 1)
                main_idx += 1
                return main_scans[idx]
            idx = min(rescan_idx, len(rescan_scans) - 1)
            rescan_idx += 1
            return rescan_scans[idx]

        with mock.patch.object(scan, "_collect_project_actions", side_effect=_fake_collect):
            with mock.patch.object(scan, "kick_execution_action") as kick_mock:
                with mock.patch.object(scan, "_max_kicks_per_cycle", return_value=3):
                    with mock.patch(
                        "asana_ops_poller._auto_kick_enabled",
                        return_value=True,
                    ):
                        result = scan.scan_execution_and_kick(
                            project_gids=["P1"],
                            token="tok",
                            dry_run=False,
                            cursor_kick=True,
                        )
        self.assertEqual(kick_mock.call_count, 2)
        self.assertEqual(result.kicks, 2)
        self.assertFalse(result.deferred)

    def test_stops_on_kick_no_progress(self) -> None:
        same = {
            "epic_gid": "E1",
            "state": "needs_pm_kick",
            "reason": "no_worker_subs",
            "pm_child_gid": "PM",
        }
        with mock.patch.object(
            scan,
            "_collect_project_actions",
            side_effect=[[same], [same]],
        ):
            with mock.patch.object(scan, "kick_execution_action") as kick_mock:
                with mock.patch(
                    "asana_ops_poller._auto_kick_enabled",
                    return_value=True,
                ):
                    with mock.patch(
                        "execution_stuck_escalate.check_and_emit_stuck",
                        return_value="WARN",
                    ) as stuck_mock:
                        result = scan.scan_execution_and_kick(
                            project_gids=["P1"],
                            token="tok",
                            dry_run=False,
                            cursor_kick=True,
                        )
        self.assertEqual(kick_mock.call_count, 1)
        self.assertEqual(result.kicks, 1)
        self.assertTrue(result.no_progress)
        self.assertFalse(result.deferred)
        self.assertEqual(result.stuck_level, "WARN")
        stuck_mock.assert_called_once()

    def test_defers_when_max_kicks_reached(self) -> None:
        kick1 = {
            "epic_gid": "E1",
            "state": "needs_worker_kick",
            "pm_child_gid": "PM",
            "worker_sub_gid": "W1",
            "reason": "incomplete_worker_without_comment",
        }
        kick2 = {
            "epic_gid": "E1",
            "state": "needs_pm_complete",
            "pm_child_gid": "PM",
            "worker_sub_gid": "W1",
            "reason": "worker_comment_without_complete",
        }

        def _collect(_projects, *, token, dry_run, log_scan=True, tick_stuck=True):  # noqa: ANN001
            if not hasattr(_collect, "n"):
                _collect.n = 0
            _collect.n += 1
            if _collect.n == 1:
                return [kick1]
            if _collect.n == 2:
                return [kick2]
            if _collect.n >= 3:
                return [kick2]
            return []

        with mock.patch.object(scan, "_collect_project_actions", side_effect=_collect):
            with mock.patch.object(scan, "kick_execution_action"):
                with mock.patch.object(scan, "_max_kicks_per_cycle", return_value=1):
                    with mock.patch(
                        "asana_ops_poller._auto_kick_enabled",
                        return_value=True,
                    ):
                        result = scan.scan_execution_and_kick(
                            project_gids=["P1"],
                            token="tok",
                            dry_run=False,
                            cursor_kick=True,
                        )
        self.assertEqual(result.kicks, 1)
        self.assertTrue(result.deferred)
        self.assertFalse(result.no_progress)


class WatchSleepTests(unittest.TestCase):
    def test_deferred_sleep_is_zero(self) -> None:
        import asana_ops_runner as runner  # noqa: WPS433

        result = runner.CycleResult(code=0, execution_deferred=True)
        self.assertEqual(runner._watch_sleep_seconds(interval=60, result=result), 0)

    def test_inflight_uses_fast_poll(self) -> None:
        import asana_ops_runner as runner  # noqa: WPS433

        result = runner.CycleResult(code=0, execution_inflight=True)
        with mock.patch.dict(os.environ, {"ORG_OPS_FAST_POLL_SEC": "7"}, clear=False):
            self.assertEqual(runner._watch_sleep_seconds(interval=60, result=result), 7)

    def test_no_progress_uses_full_interval(self) -> None:
        import asana_ops_runner as runner  # noqa: WPS433

        result = runner.CycleResult(code=0, execution_no_progress=True)
        self.assertEqual(runner._watch_sleep_seconds(interval=60, result=result), 60)

    def test_escalated_uses_full_interval(self) -> None:
        import asana_ops_runner as runner  # noqa: WPS433

        result = runner.CycleResult(code=0, execution_stuck_level="ESCALATE")
        self.assertEqual(runner._watch_sleep_seconds(interval=60, result=result), 60)


class ExecutionPromptTests(unittest.TestCase):
    def test_execution_prompt_includes_kick(self) -> None:
        from cursor_epic_dispatch import build_execution_prompt  # noqa: WPS433

        prompt = build_execution_prompt("EPIC", "planning_approval")
        self.assertIn("task_dispatcher.py", prompt)
        self.assertIn("--kick -y", prompt)


if __name__ == "__main__":
    unittest.main()
