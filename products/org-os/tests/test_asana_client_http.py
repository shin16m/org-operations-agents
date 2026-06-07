"""Tests for injectable HTTP boundary in asana_client."""
from __future__ import annotations

import unittest

from org_os import asana_client

from .fake_http import FakeAsanaBackend
from .test_helpers import env_patch, epic_task


class AsanaClientHttpTests(unittest.TestCase):
    def setUp(self) -> None:
        self.env = env_patch()
        self.env.start()
        self.backend = FakeAsanaBackend({"EPIC1": epic_task()}, project_gid="PROJ")
        asana_client.set_http_handlers(get=self.backend.get, put=self.backend.put)

    def tearDown(self) -> None:
        asana_client.reset_http_handlers()
        self.env.stop()

    def test_fetch_task_without_network(self) -> None:
        task = asana_client.fetch_task("EPIC1", token="tok")
        self.assertEqual(asana_client.read_os_state(task), "Ready")

    def test_set_os_state_updates_fake_store(self) -> None:
        asana_client.set_os_state("EPIC1", "Running", token="tok", dry_run=False)
        task = asana_client.fetch_task("EPIC1", token="tok")
        self.assertEqual(asana_client.read_os_state(task), "Running")

    def test_list_project_tasks(self) -> None:
        rows = asana_client.list_project_tasks("PROJ", token="tok")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["gid"], "EPIC1")

    def test_is_watch_epic(self) -> None:
        task = epic_task(agent="AI", task_type="Epic")
        self.assertTrue(asana_client.is_watch_epic(task))
        self.assertFalse(asana_client.is_watch_epic(epic_task(agent="human")))


if __name__ == "__main__":
    unittest.main()
