#!/usr/bin/env python3
"""Tests for create_retrospective_intake_tasks requester enforcement."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import create_retrospective_intake_tasks as crt  # noqa: E402


class RequesterNotesTests(unittest.TestCase):
    def test_placeholder_not_ok(self) -> None:
        self.assertFalse(crt.requester_notes_ok(crt.REQUESTER_PLACEHOLDER))

    def test_nonempty_ok(self) -> None:
        self.assertTrue(crt.requester_notes_ok("承認します"))


if __name__ == "__main__":
    unittest.main()
