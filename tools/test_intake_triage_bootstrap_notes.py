#!/usr/bin/env python3
"""Tests for bootstrap Epic notes two-layer assembly."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
OPT = ROOT / "skills/platform/asana-buddy/optional"
for p in (str(TOOLS), str(OPT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from asana_program_common import validate_notes_two_layer  # noqa: E402
from intake_triage import bootstrap_notes_from_epic_input, triage_snapshot  # noqa: E402

RETRO_NOTES = """\
## 依頼者向け（人間が最初に読む）

エピック完了後の振り返りで挙がった改善案です。

## 背景・用語（エージェント / 実装者向け）

doc-only 検証の validate スキップ記載テンプレ共通化

## ソース

- 元エピック GID: `1215473462951531`
"""

PLAIN_NOTES = """\
# 背景

本番 org-ops watch 起動時、auto-bootstrap が exit 2 で停止した。

# やってほしいこと

1. bootstrap_notes_from_epic_input を二層契約に合わせて修正
"""


class TestBootstrapNotesTwoLayer(unittest.TestCase):
    def _assert_valid(self, notes: str) -> None:
        errors = validate_notes_two_layer(notes, path="epic.notes_markdown")
        self.assertEqual(errors, [], msg=errors)

    def test_plain_intake_notes(self) -> None:
        snapshot = {
            "task_gid": "1215474276991066",
            "task_url": "https://app.asana.com/0/0/0/1215474276991066",
            "name": "【intake】bootstrap Epic notes 二層形式修正",
            "notes": PLAIN_NOTES,
        }
        epic_input = triage_snapshot(snapshot)["epic_input"]
        notes = bootstrap_notes_from_epic_input(epic_input, snapshot)
        self._assert_valid(notes)
        self.assertIn("auto-bootstrap が exit 2", notes)
        self.assertIn("### ソース Asana タスク", notes)

    def test_retro_style_intake_notes(self) -> None:
        snapshot = {
            "task_gid": "1215473504411409",
            "task_url": "https://app.asana.com/0/0/0/1215473504411409",
            "name": "【intake】doc-only 検証",
            "notes": RETRO_NOTES,
        }
        epic_input = triage_snapshot(snapshot)["epic_input"]
        notes = bootstrap_notes_from_epic_input(epic_input, snapshot)
        self._assert_valid(notes)
        self.assertTrue(notes.index("## 依頼者向け") < notes.index("## 背景・用語"))
        self.assertIn("振り返りで挙がった改善案", notes)
        self.assertIn("doc-only 検証", notes)


if __name__ == "__main__":
    unittest.main()
