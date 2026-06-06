#!/usr/bin/env python3
"""Tests for PM review gate opt-in (default skip)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
ASANA_OPT = TOOLS.parent / "skills/platform/asana-buddy/optional"
for p in (str(TOOLS), str(ASANA_OPT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import pm_review_gate_util as util  # noqa: E402


class HumanReviewGateRequestedTests(unittest.TestCase):
    def test_default_false(self) -> None:
        self.assertFalse(util.human_review_gate_requested())

    def test_cli_flag(self) -> None:
        self.assertTrue(util.human_review_gate_requested(cli_flag=True))

    def test_plan_flag(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump({"human_review_gate": True, "subtasks": []}, fh)
            path = Path(fh.name)
        try:
            self.assertTrue(util.human_review_gate_requested(plan_path=path))
        finally:
            path.unlink(missing_ok=True)

    def test_env_flag(self) -> None:
        with mock.patch.dict("os.environ", {"ORG_OPS_PM_REVIEW_GATE": "1"}):
            self.assertTrue(util.human_review_gate_requested())


class FindPmAssignReviewGateTests(unittest.TestCase):
    def test_matches_assign_gate_title_only(self) -> None:
        subs = [
            {"gid": "1", "name": "【レビュー】サブ構成・担当割り当て", "completed": False},
            {"gid": "2", "name": "【レビュー】other", "completed": False},
        ]
        with mock.patch("asana_program_common.list_subtasks", return_value=subs):
            found = util.find_pm_assign_review_gate_sub("P", "tok")
        self.assertEqual(found["gid"], "1")

    def test_none_when_no_gate(self) -> None:
        with mock.patch("asana_program_common.list_subtasks", return_value=[]):
            self.assertIsNone(util.find_pm_assign_review_gate_sub("P", "tok"))


class CheckPmReviewGateCliTests(unittest.TestCase):
    def test_exit_zero_when_no_gate(self) -> None:
        import check_pm_review_gate as chk  # noqa: WPS433

        with mock.patch.object(chk, "load_env_from_dotfile"):
            with mock.patch.object(chk, "get_token", return_value="tok"):
                with mock.patch.object(chk, "find_pm_assign_review_gate_sub", return_value=None):
                    with mock.patch("sys.argv", ["check_pm_review_gate.py", "--parent", "P"]):
                        self.assertEqual(chk.main(), 0)


if __name__ == "__main__":
    unittest.main()
