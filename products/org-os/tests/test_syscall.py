"""Tests for org_os.syscall state transitions."""
from __future__ import annotations

import unittest
from unittest import mock

from org_os import asana_client, syscall

from .test_helpers import env_patch, epic_task


class SyscallTransitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.env = env_patch()
        self.env.start()

    def tearDown(self) -> None:
        self.env.stop()

    def test_start_requires_ready(self) -> None:
        task = epic_task(os_state="Running")
        with mock.patch.object(asana_client, "fetch_task", return_value=task):
            with self.assertRaises(ValueError) as ctx:
                syscall.start("EPIC1", agent_id="workflow-orchestrator")
        self.assertIn("Ready", str(ctx.exception))

    def test_start_transitions_to_running(self) -> None:
        task = epic_task(os_state="Ready")
        with mock.patch.object(asana_client, "fetch_task", return_value=task):
            with mock.patch.object(asana_client, "set_os_state") as set_state:
                with mock.patch.object(asana_client, "set_suspend_reason") as clr_sr:
                    with mock.patch.object(asana_client, "set_approval_required") as clr_ap:
                        out = syscall.start("EPIC1", agent_id="workflow-orchestrator", dry_run=True)
        self.assertEqual(out["os_state"], "Running")
        set_state.assert_called_once_with("EPIC1", "Running", dry_run=True)
        clr_sr.assert_called_once()
        clr_ap.assert_called_once()

    def test_suspend_invalid_reason(self) -> None:
        with self.assertRaises(ValueError):
            syscall.suspend("EPIC1", "bad_reason", dry_run=True)

    def test_suspend_from_running(self) -> None:
        task = epic_task(os_state="Running")
        with mock.patch.object(asana_client, "fetch_task", return_value=task):
            with mock.patch.object(asana_client, "set_os_state") as set_state:
                with mock.patch.object(asana_client, "set_suspend_reason"):
                    with mock.patch.object(asana_client, "set_approval_required") as set_ap:
                        out = syscall.suspend("EPIC1", "Approval", ref="SUB1", dry_run=True)
        self.assertEqual(out["os_state"], "Waiting")
        self.assertEqual(out["suspend_reason"], "Approval")
        set_state.assert_called_once_with("EPIC1", "Waiting", dry_run=True)
        set_ap.assert_called_once_with("EPIC1", "Yes", dry_run=True)

    def test_resume_requires_waiting(self) -> None:
        task = epic_task(os_state="Ready")
        with mock.patch.object(asana_client, "fetch_task", return_value=task):
            with self.assertRaises(ValueError):
                syscall.resume("EPIC1", dry_run=True)

    def test_complete_from_ready(self) -> None:
        task = epic_task(os_state="Ready")
        with mock.patch.object(asana_client, "fetch_task", return_value=task):
            with mock.patch.object(asana_client, "set_os_state") as set_state:
                with mock.patch.object(asana_client, "set_suspend_reason"):
                    with mock.patch.object(asana_client, "set_approval_required"):
                        out = syscall.complete("EPIC1", dry_run=True)
        self.assertEqual(out["os_state"], "Done")
        set_state.assert_called_once_with("EPIC1", "Done", dry_run=True)


if __name__ == "__main__":
    unittest.main()
