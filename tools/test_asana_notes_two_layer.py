#!/usr/bin/env python3
"""Unit tests for Asana task notes two-layer contract."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPT = ROOT / "skills/platform/asana-buddy/optional"
if str(OPT) not in sys.path:
    sys.path.insert(0, str(OPT))

from asana_program_common import (  # noqa: E402
    assemble_subtask_notes,
    notes_from_legacy_body,
    validate_comment_body_not_legacy_task_notes,
    validate_notes_two_layer,
)


class TestAssembleSubtaskNotes(unittest.TestCase):
    def test_two_layer_format(self) -> None:
        notes = assemble_subtask_notes(
            "技術的背景",
            "人間向けの概要です。",
            "テストが green になること。",
            department="development",
        )
        self.assertIn("## 依頼者向け", notes)
        self.assertIn("## 背景・用語", notes)
        self.assertIn("人間向けの概要です。", notes)
        self.assertIn("### 背景\n技術的背景", notes)
        self.assertTrue(notes.index("## 依頼者向け") < notes.index("## 背景・用語"))

    def test_validate_passes(self) -> None:
        notes = assemble_subtask_notes("bg", "summary", "done")
        self.assertEqual(validate_notes_two_layer(notes), [])

    def test_validate_rejects_legacy(self) -> None:
        legacy = "## 背景\nx\n\n## 概要\ny\n\n## 完了条件\nz"
        errors = validate_notes_two_layer(legacy)
        self.assertTrue(errors)
        self.assertIn("notes-two-layer", errors[0])

    def test_legacy_body_migration(self) -> None:
        legacy = "## 背景\nold bg\n\n## 概要\nold sm\n\n## 完了条件\nold dw"
        notes = notes_from_legacy_body(legacy)
        self.assertIn("## 依頼者向け", notes)
        self.assertEqual(validate_notes_two_layer(notes), [])


class TestCommentBodyLegacyGuard(unittest.TestCase):
    def test_rejects_legacy_task_notes_as_comment(self) -> None:
        err = validate_comment_body_not_legacy_task_notes("## 背景\nfoo")
        self.assertIsNotNone(err)

    def test_allows_action_style_body(self) -> None:
        err = validate_comment_body_not_legacy_task_notes("## 実施内容\n- did work")
        self.assertIsNone(err)


if __name__ == "__main__":
    unittest.main()
