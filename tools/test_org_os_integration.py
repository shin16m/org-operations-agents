#!/usr/bin/env python3
"""Integration smoke: org-os syscall chain on mock Asana (C2-2)."""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ORG_OS_SRC = ROOT / "products/org-os/src"
ORG_OS_TESTS = ROOT / "products/org-os/tests"

# python tools/test_*.py puts tools/ on sys.path[0] and shadows org_os package.
if sys.path and Path(sys.path[0]).resolve() == TOOLS.resolve():
    sys.path.pop(0)
_stale = sys.modules.get("org_os")
if _stale is not None and not hasattr(_stale, "__path__"):
    del sys.modules["org_os"]

for p in (str(ORG_OS_SRC), str(ORG_OS_TESTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

from fake_http import FakeAsanaBackend  # noqa: E402
from test_helpers import TEST_ENV, epic_task  # noqa: E402

from org_os import asana_client, syscall  # noqa: E402


class OrgOsIntegrationSmokeTests(unittest.TestCase):
    """init_epic → suspend → resume → complete without network."""

    def setUp(self) -> None:
        self.env = mock.patch.dict(os.environ, TEST_ENV, clear=False)
        self.env.start()
        task = epic_task(gid="EPIC1", os_state="Ready")
        self.backend = FakeAsanaBackend({"EPIC1": task}, project_gid="PROJ")
        asana_client.set_http_handlers(get=self.backend.get, put=self.backend.put)

    def tearDown(self) -> None:
        asana_client.reset_http_handlers()
        self.env.stop()

    def test_syscall_lifecycle_chain(self) -> None:
        out_init = syscall.init_epic("EPIC1", dry_run=False)
        self.assertEqual(out_init["os_state"], "Ready")

        out_start = syscall.start("EPIC1", agent_id="workflow-orchestrator", dry_run=False)
        self.assertEqual(out_start["os_state"], "Running")
        task = asana_client.fetch_task("EPIC1")
        self.assertEqual(asana_client.read_os_state(task), "Running")

        out_suspend = syscall.suspend("EPIC1", "Approval", ref="SUB1", dry_run=False)
        self.assertEqual(out_suspend["os_state"], "Waiting")
        task = asana_client.fetch_task("EPIC1")
        self.assertEqual(asana_client.read_os_state(task), "Waiting")

        out_resume = syscall.resume("EPIC1", ref="SUB1", dry_run=False)
        self.assertEqual(out_resume["os_state"], "Ready")
        task = asana_client.fetch_task("EPIC1")
        self.assertEqual(asana_client.read_os_state(task), "Ready")

        out_start2 = syscall.start("EPIC1", agent_id="workflow-orchestrator", dry_run=False)
        self.assertEqual(out_start2["os_state"], "Running")

        out_complete = syscall.complete("EPIC1", dry_run=False)
        self.assertEqual(out_complete["os_state"], "Done")
        task = asana_client.fetch_task("EPIC1")
        self.assertEqual(asana_client.read_os_state(task), "Done")


if __name__ == "__main__":
    unittest.main()
