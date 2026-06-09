#!/usr/bin/env python3
"""RETIRED — planning-stuck tests depended on asana_ops_poller (removed 2026-06-09)."""

from __future__ import annotations

import unittest


@unittest.skip("Asana automation retired — asana_ops_poller removed; see chat-driven-ops.md")
class PlanningStuckTests(unittest.TestCase):
    def test_retired(self) -> None:
        pass
