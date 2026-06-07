#!/usr/bin/env python3
"""Tests for L2 dispatch sort by Execution Order CF."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
for p in (str(TOOLS), str(TOOLS.parent / "skills/platform/asana-buddy/optional")):
    if p not in sys.path:
        sys.path.insert(0, p)

import task_dispatcher as td  # noqa: E402


class PickTargetDependencyTests(unittest.TestCase):
    def test_skips_dependency_blocked_child(self) -> None:
        children = [
            {"gid": "100", "department": "development", "execution_order": 1, "name": "first"},
            {"gid": "200", "department": "development", "execution_order": 2, "name": "second"},
        ]
        with unittest.mock.patch.object(td, "_epic_children", return_value=children):
            with unittest.mock.patch.object(td, "has_open_dependencies", side_effect=[True, False]):
                picked = td.pick_target(epic_gid="EPIC", token="tok", task_gid=None, department=None)
        self.assertIsNotNone(picked)
        self.assertEqual(picked["gid"], "200")


class SortExecutionOrderTests(unittest.TestCase):
    def test_execution_order_before_gid(self) -> None:
        rows = [
            {"gid": "200", "department": "development", "execution_order": 4},
            {"gid": "100", "department": "development", "execution_order": 2},
        ]
        sorted_rows = td._sort_execution(rows)
        self.assertEqual(sorted_rows[0]["gid"], "100")
        self.assertEqual(sorted_rows[1]["gid"], "200")

    def test_missing_execution_order_sorts_last(self) -> None:
        rows = [
            {"gid": "100", "department": "development", "execution_order": None},
            {"gid": "200", "department": "development", "execution_order": 1},
        ]
        sorted_rows = td._sort_execution(rows)
        self.assertEqual(sorted_rows[0]["gid"], "200")


if __name__ == "__main__":
    unittest.main()
