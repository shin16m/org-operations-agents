#!/usr/bin/env python3
"""Tests for L3b worker kick in-flight guard."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
for p in (str(TOOLS), str(TOOLS.parent / "skills/platform/asana-buddy/optional")):
    if p not in sys.path:
        sys.path.insert(0, p)

import execution_resume_scan as scan  # noqa: E402
import worker_kick_inflight as inflight  # noqa: E402


class WorkerKickInflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = TOOLS / "output" / "platform" / "worker-inflight-test"
        self._tmpdir.mkdir(parents=True, exist_ok=True)
        self._orig_dir = inflight.INFLIGHT_DIR
        inflight.INFLIGHT_DIR = self._tmpdir

    def tearDown(self) -> None:
        inflight.INFLIGHT_DIR = self._orig_dir
        for p in self._tmpdir.glob("*.json"):
            p.unlink(missing_ok=True)

    def test_claim_blocks_duplicate(self) -> None:
        ok1, _ = inflight.claim_worker_kick(
            "W1", epic_gid="E1", pm_child_gid="PM1", tool="test"
        )
        ok2, reason2 = inflight.claim_worker_kick(
            "W1", epic_gid="E1", pm_child_gid="PM1", tool="test"
        )
        self.assertTrue(ok1)
        self.assertFalse(ok2)
        self.assertIn("worker_inflight", reason2)

    def test_release_allows_reclaim(self) -> None:
        inflight.claim_worker_kick("W2", epic_gid="E1", pm_child_gid="PM1", tool="test")
        inflight.release_worker_kick("W2")
        ok, _ = inflight.claim_worker_kick("W2", epic_gid="E1", pm_child_gid="PM1", tool="test")
        self.assertTrue(ok)

    def test_classify_wait_worker_inflight(self) -> None:
        inflight.claim_worker_kick("W3", epic_gid="EPIC", pm_child_gid="PM", tool="test")
        workers = [{"gid": "W3", "name": "worker", "assignee": "developer"}]
        with mock.patch.object(scan, "_worker_subs", return_value=workers):
            with mock.patch.object(scan, "_find_review_sub", return_value={"gid": "R", "completed": True}):
                with mock.patch.object(scan, "fetch_task", return_value={"notes": "チーム: development"}):
                    with mock.patch.object(scan, "has_agent_comment", return_value=False):
                        out = scan.classify_pm_child(
                            epic_gid="EPIC",
                            pm_child={"gid": "PM", "name": "dev", "department": "development"},
                            token="tok",
                        )
        self.assertEqual(out["state"], "wait_worker_inflight")


if __name__ == "__main__":
    unittest.main()
