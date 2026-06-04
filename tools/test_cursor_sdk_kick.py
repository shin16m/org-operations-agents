#!/usr/bin/env python3
"""Unit tests for cursor_sdk_kick isolation decisions."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import cursor_sdk_kick as kick  # noqa: E402


class KickIsolationTests(unittest.TestCase):
    def test_isolation_on_windows_by_default(self) -> None:
        with mock.patch.object(kick.sys, "platform", "win32"):
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop(kick.KICK_WORKER_ENV, None)
                os.environ.pop("ORG_OPS_KICK_ISOLATE", None)
                self.assertTrue(kick.isolation_enabled())

    def test_isolation_off_in_worker(self) -> None:
        with mock.patch.object(kick.sys, "platform", "win32"):
            with mock.patch.dict(os.environ, {kick.KICK_WORKER_ENV: "1"}, clear=False):
                self.assertFalse(kick.isolation_enabled())

    def test_isolation_off_on_linux(self) -> None:
        with mock.patch.object(kick.sys, "platform", "linux"):
            self.assertFalse(kick.isolation_enabled())

    def test_runtime_auto_defaults_local_without_repo_url(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ORG_OPS_KICK_RUNTIME", None)
            os.environ.pop("ORG_OPS_REPO_URL", None)
            self.assertEqual(kick.kick_runtime_mode(), "local")

    def test_runtime_auto_picks_cloud_with_repo_url(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"ORG_OPS_REPO_URL": "https://github.com/example/repo.git"},
            clear=False,
        ):
            os.environ.pop("ORG_OPS_KICK_RUNTIME", None)
            self.assertEqual(kick.kick_runtime_mode(), "cloud")

    def test_kick_prompt_skip_without_api_key(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CURSOR_API_KEY", None)
            code = kick.kick_prompt("test", label="TEST", no_api_key_exit=2)
            self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
