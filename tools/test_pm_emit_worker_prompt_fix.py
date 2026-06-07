#!/usr/bin/env python3
"""Tests for pm_emit_worker_prompt fix context injection."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import pm_emit_worker_prompt as pep  # noqa: E402


class FixContextTests(unittest.TestCase):
    def test_non_fix_sub_has_no_context(self) -> None:
        out = pep._fix_context_block(
            parent_gid="PM123",
            sub_name="developer — code",
            sub_notes="",
        )
        self.assertEqual(out, "")

    def test_fix_sub_includes_smoke_path(self) -> None:
        notes = "## 修正依頼\n\n- review JSON: `output/development/reviews/x.json`\n"
        out = pep._fix_context_block(
            parent_gid="PM123",
            sub_name="[fix] developer — code (R1)",
            sub_notes=notes,
        )
        self.assertIn("fix コンテキスト", out)
        self.assertIn("output/development/smoke/PM123.md", out)
        self.assertIn("review JSON", out)


if __name__ == "__main__":
    unittest.main()
