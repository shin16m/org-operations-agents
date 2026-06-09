#!/usr/bin/env python3
"""RETIRED — runner ordering tests depended on asana_ops_runner (removed 2026-06-09)."""

from __future__ import annotations

import unittest


@unittest.skip("Asana automation retired — asana_ops_runner removed; see chat-driven-ops.md")
class RunnerApprovalHelperOrderTests(unittest.TestCase):
    def test_retired(self) -> None:
        pass
