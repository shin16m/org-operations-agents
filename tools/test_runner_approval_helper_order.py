#!/usr/bin/env python3
"""Tests for runner B→C approval_helper ordering (intake 1215437709736921)."""

from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
ASANA_OPT = TOOLS.parent / "skills/platform/asana-buddy/optional"
for p in (str(TOOLS), str(ASANA_OPT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import asana_ops_poller as poller  # noqa: E402
import asana_ops_runner as runner  # noqa: E402
import asana_ops_sessions as sessions  # noqa: E402


class ApprovalSubGidResumeTests(unittest.TestCase):
    def test_resumable_when_sub_completed(self) -> None:
        session = {"approval_sub_gid": "SUB1", "parent_gid": "P1"}
        with mock.patch(
            "asana_program_common.fetch_task",
            return_value={"gid": "SUB1", "completed": True},
        ):
            self.assertEqual(sessions.approval_sub_resume_status(session, "tok"), "resumable")
            self.assertEqual(poller.check_session_resume(session, "tok"), "approved")

    def test_pending_when_sub_open(self) -> None:
        session = {"approval_sub_gid": "SUB1"}
        with mock.patch(
            "asana_program_common.fetch_task",
            return_value={"gid": "SUB1", "completed": False},
        ):
            self.assertEqual(poller.check_session_resume(session, "tok"), "pending")

    def test_ignores_marker_ambiguity(self) -> None:
        """approval_sub_gid wins even if marker search would differ."""
        session = {
            "approval_sub_gid": "CORRECT",
            "parent_gid": "EPIC",
            "marker": "【承認】",
        }
        with mock.patch(
            "asana_program_common.fetch_task",
            return_value={"gid": "CORRECT", "completed": True},
        ):
            self.assertEqual(poller.check_session_resume(session, "tok"), "approved")


class ScanProjectsHelperTests(unittest.TestCase):
    def test_approved_session_runs_helper_not_auto_kick(self) -> None:
        session = {
            "session_id": "S1",
            "state": "suspended",
            "parent_gid": "PM_CHILD",
            "approval_sub_gid": "SUB",
            "gate_kind": "pm_review_gate",
            "_path": "x.json",
        }
        buf = io.StringIO()
        with mock.patch.object(poller, "load_sessions", return_value=[session]):
            with mock.patch.object(poller, "check_session_resume", return_value="approved"):
                with mock.patch.object(poller, "run_session_approval_helper", return_value=0) as helper:
                    with mock.patch.object(poller, "_session_auto_kick") as kick:
                        with redirect_stdout(buf):
                            poller.scan_projects(
                                project_gids=[],
                                token="tok",
                                dry_run=True,
                                human=False,
                                trigger_gid=None,
                            )
        helper.assert_called_once()
        kick.assert_not_called()
        out = buf.getvalue()
        self.assertIn("RESUME", out)
        self.assertIn("HELPER", out)


class RunnerHelperParentTests(unittest.TestCase):
    def test_helper_pass_uses_wait_target_parent(self) -> None:
        session = {
            "parent_gid": "PM_CHILD",
            "epic_gid": "EPIC",
            "approval_sub_gid": "SUB",
            "gate_kind": "pm_review_gate",
        }
        captured: list[list[str]] = []

        def fake_run(cmd, **kwargs):  # noqa: ANN003
            captured.append(cmd)
            class R:
                returncode = 0

            return R()

        with mock.patch.object(runner, "load_env_from_dotfile"):
            with mock.patch.object(runner, "get_token", return_value="tok"):
                with mock.patch.object(
                    runner.asana_ops_sessions,
                    "load_suspended_sessions",
                    return_value=[session],
                ):
                    with mock.patch.object(
                        runner.asana_ops_sessions,
                        "check_session_status",
                        return_value={"status": "resumable"},
                    ):
                        with mock.patch("subprocess.run", side_effect=fake_run):
                            count = runner.run_approval_helper_pass(dry_run=False)
        self.assertEqual(count, 1)
        self.assertIn("--parent", captured[0])
        idx = captured[0].index("--parent")
        self.assertEqual(captured[0][idx + 1], "PM_CHILD")


class RunnerCycleOrderTests(unittest.TestCase):
    def test_cycle_order_ssot_matches_approval_flow(self) -> None:
        expected = (
            "approval_helper_pass",
            "scan_projects",
            "scan_resume_and_dispatch",
            "scan_execution_and_kick",
            "archive_resumable_sessions",
        )
        self.assertEqual(runner.CYCLE_ORDER, expected)

    def test_run_cycle_invokes_steps_in_order(self) -> None:
        calls: list[str] = []

        def _helper(**kwargs):  # noqa: ANN003
            calls.append("approval_helper_pass")
            return 0

        def _scan_projects(**kwargs):  # noqa: ANN003
            calls.append("scan_projects")
            return 0

        def _scan_resume(**kwargs):  # noqa: ANN003
            calls.append("scan_resume_and_dispatch")
            return 0

        def _scan_execution(**kwargs):  # noqa: ANN003
            calls.append("scan_execution_and_kick")
            return 0

        def _archive(token, *, dry_run):  # noqa: ANN001
            calls.append("archive_resumable_sessions")
            return 0

        with mock.patch.object(runner, "run_approval_helper_pass", side_effect=_helper):
            with mock.patch.object(runner, "scan_projects", side_effect=_scan_projects):
                with mock.patch.object(runner, "scan_resume_and_dispatch", side_effect=_scan_resume):
                    with mock.patch(
                        "execution_resume_scan.scan_execution_and_kick",
                        side_effect=_scan_execution,
                    ):
                        with mock.patch.object(
                            runner.asana_ops_sessions,
                            "archive_resumable_sessions",
                            side_effect=_archive,
                        ):
                            with mock.patch.object(runner, "load_env_from_dotfile"):
                                with mock.patch.object(runner, "get_token", return_value="tok"):
                                    with mock.patch.object(
                                        runner,
                                        "_auto_kick_enabled",
                                        return_value=False,
                                    ):
                                        rc = runner.run_cycle(
                                            project_gids=["P1"],
                                            dry_run=True,
                                            yes=False,
                                            human=True,
                                            max_ng=3,
                                            cursor_kick=False,
                                        )
        self.assertEqual(rc, 0)
        self.assertEqual(calls, list(runner.CYCLE_ORDER))


if __name__ == "__main__":
    unittest.main()
