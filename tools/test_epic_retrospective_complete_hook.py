#!/usr/bin/env python3
"""Tests for epic_retrospective_complete_hook."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import epic_retrospective_complete_hook as hook  # noqa: E402


class BuildWarnCommentTests(unittest.TestCase):
    def test_ok_no_comment(self) -> None:
        ev = hook.RetroGateEvaluation(kind="ok", message="ok")
        self.assertIsNone(hook.build_warn_comment(ev))

    def test_missing_comment(self) -> None:
        ev = hook.RetroGateEvaluation(kind="missing", message="gate missing")
        text = hook.build_warn_comment(ev)
        self.assertIn(hook.WARN_MARKER, text or "")
        self.assertIn("gate missing", text or "")


class RunHookTests(unittest.TestCase):
    @mock.patch.dict("os.environ", {}, clear=True)
    @mock.patch.object(hook, "post_warn_comment")
    @mock.patch.object(hook, "evaluate_retro_gate")
    def test_missing_warn_non_blocking(
        self,
        evaluate: mock.Mock,
        post: mock.Mock,
    ) -> None:
        evaluate.return_value = hook.RetroGateEvaluation(
            kind="missing",
            message="missing",
            check_exit=0,
        )
        rc = hook.run_epic_retrospective_gate_hook("EPIC", token="tok")
        self.assertEqual(rc, 0)
        post.assert_called_once()

    @mock.patch.dict("os.environ", {"ORG_OPS_RETRO_COMPLETE_BLOCK": "1"}, clear=True)
    @mock.patch.object(hook, "post_warn_comment")
    @mock.patch.object(hook, "evaluate_retro_gate")
    def test_pending_blocks_when_opt_in(
        self,
        evaluate: mock.Mock,
        post: mock.Mock,
    ) -> None:
        evaluate.return_value = hook.RetroGateEvaluation(
            kind="pending",
            message="pending",
            check_exit=1,
        )
        rc = hook.run_epic_retrospective_gate_hook("EPIC", token="tok")
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
