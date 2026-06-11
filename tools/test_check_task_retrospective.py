#!/usr/bin/env python3
"""Tests for check_task_retrospective completion_score enforcement."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import check_task_retrospective as chk  # noqa: E402


class CheckTaskRetrospectiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)
        self._orig_out = chk.OUT
        chk.OUT = self.out

    def tearDown(self) -> None:
        chk.OUT = self._orig_out
        self.tmp.cleanup()

    def _write(self, gid: str, data: dict) -> None:
        path = self.out / f"{gid}-retro.json"
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_missing_file_exit_1(self) -> None:
        rc = chk.check_retrospective("missing", require_completion_score=True)
        self.assertEqual(rc, 1)

    def test_missing_completion_score_exit_1(self) -> None:
        self._write("T1", {"task_gid": "T1", "agent": "developer"})
        rc = chk.check_retrospective("T1", require_completion_score=True)
        self.assertEqual(rc, 1)

    def test_invalid_completion_score_exit_1(self) -> None:
        self._write("T2", {"task_gid": "T2", "completion_score": 150})
        rc = chk.check_retrospective("T2", require_completion_score=True)
        self.assertEqual(rc, 1)

    def test_valid_completion_score_exit_0(self) -> None:
        self._write(
            "T3",
            {"task_gid": "T3", "agent": "developer", "completion_score": 85.5},
        )
        rc = chk.check_retrospective("T3", require_completion_score=True)
        self.assertEqual(rc, 0)

    def test_opt_out_completion_score(self) -> None:
        self._write("T4", {"task_gid": "T4", "agent": "developer"})
        rc = chk.check_retrospective("T4", require_completion_score=False)
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
