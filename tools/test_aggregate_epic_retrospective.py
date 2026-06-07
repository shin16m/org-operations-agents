#!/usr/bin/env python3
"""Tests for aggregate_epic_retrospective --parent subtree filter."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import aggregate_epic_retrospective as agg  # noqa: E402


class LoadTaskRetrosTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)
        self._orig_out = agg.OUT
        agg.OUT = self.out

    def tearDown(self) -> None:
        agg.OUT = self._orig_out
        self.tmp.cleanup()

    def _write_retro(self, gid: str) -> None:
        path = self.out / f"{gid}-retro.json"
        path.write_text(
            json.dumps({"task_gid": gid, "agent": "dev", "intake_candidates": ["x"]}),
            encoding="utf-8",
        )

    def test_filters_by_epic_gids(self) -> None:
        self._write_retro("IN")
        self._write_retro("OUT")
        rows = agg.load_task_retros(epic_gids={"IN", "EPIC"})
        gids = {r["task_gid"] for r in rows}
        self.assertEqual(gids, {"IN"})

    def test_no_filter_includes_all(self) -> None:
        self._write_retro("A")
        self._write_retro("B")
        rows = agg.load_task_retros(epic_gids=None)
        self.assertEqual(len(rows), 2)


class CollectSubtaskGidsTests(unittest.TestCase):
    @mock.patch("asana_program_common.list_subtasks")
    def test_recursive_collect(self, list_sub: mock.Mock) -> None:
        list_sub.side_effect = lambda gid, _token: {
            "EPIC": [{"gid": "L2"}, {"gid": "L2B"}],
            "L2": [{"gid": "W1"}],
            "L2B": [],
            "W1": [{"gid": "R1"}],
            "R1": [],
        }.get(gid, [])

        gids = agg.collect_subtask_gids("EPIC", "tok")
        self.assertEqual(gids, {"EPIC", "L2", "L2B", "W1", "R1"})


if __name__ == "__main__":
    unittest.main()
