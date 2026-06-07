"""Tests for org_os.queue filters."""
from __future__ import annotations

import unittest
from unittest import mock

from org_os import queue

from .test_helpers import env_patch, epic_task


class QueueFilterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.env = env_patch()
        self.env.start()

    def tearDown(self) -> None:
        self.env.stop()

    def test_ready_queue_filters_approval_yes(self) -> None:
        tasks = [
            epic_task(gid="E1", os_state="Ready", approval="No", created_at="2026-01-02"),
            epic_task(gid="E2", os_state="Ready", approval="Yes", created_at="2026-01-01"),
            epic_task(gid="E3", os_state="Waiting", approval="No"),
        ]
        with mock.patch.object(queue, "list_project_tasks", return_value=tasks):
            rows = queue.ready_queue("PROJ", token="tok")
        self.assertEqual([r["epic_gid"] for r in rows], ["E1"])

    def test_ready_queue_fifo_by_created_at(self) -> None:
        tasks = [
            epic_task(gid="E2", created_at="2026-01-02"),
            epic_task(gid="E1", created_at="2026-01-01"),
        ]
        with mock.patch.object(queue, "list_project_tasks", return_value=tasks):
            rows = queue.ready_queue("PROJ", token="tok")
        self.assertEqual([r["epic_gid"] for r in rows], ["E1", "E2"])

    def test_wait_list_only_waiting(self) -> None:
        tasks = [
            epic_task(gid="E1", os_state="Waiting", suspend_reason="Approval"),
            epic_task(gid="E2", os_state="Ready"),
        ]
        with mock.patch.object(queue, "list_project_tasks", return_value=tasks):
            rows = queue.wait_list("PROJ", token="tok")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["epic_gid"], "E1")
        self.assertEqual(rows[0]["suspend_reason"], "Approval")

    def test_skips_non_watch_epic(self) -> None:
        tasks = [
            epic_task(gid="E1", agent="human"),
            epic_task(gid="E2", task_type="Intake"),
        ]
        with mock.patch.object(queue, "list_project_tasks", return_value=tasks):
            self.assertEqual(queue.ready_queue("PROJ", token="tok"), [])


if __name__ == "__main__":
    unittest.main()
