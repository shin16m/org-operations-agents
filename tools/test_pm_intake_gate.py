#!/usr/bin/env python3
"""Tests for development PM intake gate (full-ui ## 依存)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import pm_intake_gate as gate  # noqa: E402

GOOD_NOTES = """\
チーム: development
profile: full-ui
担当: product-manager
状態: in_progress

## 背景
Web UI

## 依存（読み取り専用）

| 種別 | 参照 | バージョン | 提供チーム |
|------|------|------------|------------|
| UX 仕様 | `output/ux/specs/123-ux-spec.md` | v1.0 | ux |
| Figma UI | https://www.figma.com/design/abc?node-id=1 | v1.0 | ux |
"""


class PmIntakeGateTests(unittest.TestCase):
    def test_allows_lite_without_dependency(self) -> None:
        notes = "チーム: development\nprofile: lite\n"
        ok, failures = gate.check_development_intake(notes, plan_profile="lite")
        self.assertTrue(ok)
        self.assertEqual(failures, [])

    def test_blocks_full_ui_missing_dependency(self) -> None:
        notes = "チーム: development\nprofile: full-ui\n"
        ok, failures = gate.check_development_intake(notes, plan_profile="full-ui")
        self.assertFalse(ok)
        self.assertTrue(any("## 依存" in f for f in failures))

    def test_blocks_full_ui_missing_figma(self) -> None:
        notes = (
            "profile: full-ui\n\n## 依存（読み取り専用）\n\n"
            "| UX | `output/ux/specs/x.md` | v1 | ux |\n"
        )
        ok, failures = gate.check_development_intake(notes, plan_profile="full-ui")
        self.assertFalse(ok)
        self.assertTrue(any("Figma" in f for f in failures))

    def test_allows_good_full_ui_notes(self) -> None:
        ok, failures = gate.check_development_intake(GOOD_NOTES, plan_profile="full-ui")
        self.assertTrue(ok)
        self.assertEqual(failures, [])

    def test_plan_profile_triggers_gate_without_notes_profile(self) -> None:
        notes = "## 背景\nno profile header\n"
        ok, failures = gate.check_development_intake(notes, plan_profile="full-ui")
        self.assertFalse(ok)
        self.assertTrue(failures)

    def test_requires_dependency_after_profile_header(self) -> None:
        notes = (
            "## 依存（読み取り専用）\n\n"
            "| UX | `output/ux/specs/x.md` | https://www.figma.com/design/x | ux |\n\n"
            "profile: full-ui\n"
        )
        ok, failures = gate.check_development_intake(notes, plan_profile="full-ui")
        self.assertFalse(ok)
        self.assertTrue(any("after profile" in f for f in failures))


if __name__ == "__main__":
    unittest.main()
