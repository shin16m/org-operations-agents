"""Tests for org_os.env."""
from __future__ import annotations

import os
import unittest
from unittest import mock

from org_os.env import require_agent_id

from .test_helpers import TEST_ENV, env_patch


class RequireAgentIdTests(unittest.TestCase):
    def test_explicit_agent_id(self) -> None:
        with env_patch():
            self.assertEqual(require_agent_id("custom-agent"), "custom-agent")

    def test_env_agent_id(self) -> None:
        with env_patch():
            self.assertEqual(require_agent_id(None), TEST_ENV["ORG_OS_AGENT_ID"])

    def test_missing_raises(self) -> None:
        with mock.patch.dict(os.environ, {"ORG_OS_AGENT_ID": ""}, clear=False):
            with self.assertRaises(RuntimeError) as ctx:
                require_agent_id(None)
        self.assertIn("ORG_OS_AGENT_ID", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
