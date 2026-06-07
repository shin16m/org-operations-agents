#!/usr/bin/env python3
"""Unit tests for L2 execution dispatch opt-in helper."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from execution_dispatch_util import human_execution_dispatch_requested  # noqa: E402


class ExecutionDispatchOptInTests(unittest.TestCase):
    def test_default_off(self) -> None:
        self.assertFalse(human_execution_dispatch_requested())

    def test_env_on(self) -> None:
        os.environ["ORG_OPS_EXECUTION_DISPATCH_CONFIRM"] = "1"
        try:
            self.assertTrue(human_execution_dispatch_requested())
        finally:
            os.environ.pop("ORG_OPS_EXECUTION_DISPATCH_CONFIRM", None)

    def test_handoff_meta(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({"meta": {"human_execution_dispatch": True}}, f)
            path = Path(f.name)
        try:
            self.assertTrue(human_execution_dispatch_requested(handoff_path=path))
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
