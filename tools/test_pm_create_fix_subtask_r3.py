#!/usr/bin/env python3
"""Tests for pm_create_fix_subtask R3 escalation helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import pm_create_fix_subtask as fix  # noqa: E402


class R3EscalationTests(unittest.TestCase):
    def test_build_r3_comment_mentions_ssot(self) -> None:
        body = fix.build_r3_escalation_comment(
            fix_round=3,
            gate_label="code",
            review_path=Path("output/development/reviews/x.json"),
        )
        self.assertIn("R3", body)
        self.assertIn("pm-review-rework-ssot", body)

    def test_assemble_fix_notes_marks_r3(self) -> None:
        notes = fix.assemble_fix_notes(
            department="development",
            assignee="developer",
            round_n=3,
            gate_label="code",
            review={"status": "failed", "review_kind": "code", "summary": "ng"},
            review_path=Path("output/development/reviews/x.json"),
            worker_mode=None,
            done_when=None,
        )
        self.assertIn(fix.R3_ESCALATION_MARKER, notes)


if __name__ == "__main__":
    unittest.main()
