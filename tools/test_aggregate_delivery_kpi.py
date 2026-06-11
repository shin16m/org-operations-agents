#!/usr/bin/env python3
"""Tests for aggregate_delivery_kpi."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import aggregate_delivery_kpi as kpi  # noqa: E402


class AggregateDeliveryKpiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.retro_dir = self.root / "retrospectives"
        self.review_dir = self.root / "reviews"
        self.retro_dir.mkdir()
        self.review_dir.mkdir()
        self._orig_retro = kpi.RETRO_DIR
        self._orig_review = kpi.REVIEW_DIR
        kpi.RETRO_DIR = self.retro_dir
        kpi.REVIEW_DIR = self.review_dir

    def tearDown(self) -> None:
        kpi.RETRO_DIR = self._orig_retro
        kpi.REVIEW_DIR = self._orig_review
        self.tmp.cleanup()

    def test_compute_kpis_from_fixtures(self) -> None:
        (self.retro_dir / "100-retro.json").write_text(
            json.dumps({"task_gid": "100", "completion_score": 80}),
            encoding="utf-8",
        )
        (self.retro_dir / "101-retro.json").write_text(
            json.dumps({"task_gid": "101", "completion_score": 60}),
            encoding="utf-8",
        )
        (self.review_dir / "100-verification.json").write_text(
            json.dumps(
                {"review_kind": "verification", "status": "passed", "summary": "ok"}
            ),
            encoding="utf-8",
        )
        (self.review_dir / "101-verification.json").write_text(
            json.dumps(
                {"review_kind": "verification", "status": "failed", "summary": "ng"}
            ),
            encoding="utf-8",
        )
        (self.review_dir / "101-verification-fix.json").write_text(
            json.dumps(
                {
                    "review_kind": "verification",
                    "status": "passed",
                    "summary": "ok",
                }
            ),
            encoding="utf-8",
        )

        result = kpi.compute_kpis(task_gids=None)
        self.assertEqual(result["verification_total"], 2)
        self.assertEqual(result["verification_passed"], 1)
        self.assertAlmostEqual(result["first_qa_pass_rate"], 0.5)
        self.assertAlmostEqual(result["completion_score_avg"], 70.0)
        self.assertGreater(result["fix_avg_rounds"], 0)


if __name__ == "__main__":
    unittest.main()
