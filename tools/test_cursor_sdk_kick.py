#!/usr/bin/env python3
"""Unit tests for cursor_sdk_kick isolation decisions."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from subprocess import CompletedProcess
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

    def test_kick_subprocess_env_sets_pythonioencoding(self) -> None:
        env = kick._kick_subprocess_env({})
        self.assertEqual(env.get("PYTHONIOENCODING"), "utf-8")

    def test_cloud_fallback_default_on_win32(self) -> None:
        with mock.patch.object(kick.sys, "platform", "win32"):
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("ORG_OPS_KICK_FALLBACK_CLOUD", None)
                self.assertTrue(kick.cloud_fallback_enabled())

    def test_cloud_fallback_off_via_env(self) -> None:
        with mock.patch.object(kick.sys, "platform", "win32"):
            with mock.patch.dict(os.environ, {"ORG_OPS_KICK_FALLBACK_CLOUD": "0"}, clear=False):
                self.assertFalse(kick.cloud_fallback_enabled())

    def test_kick_prompt_retries_cloud_on_local_failure(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"CURSOR_API_KEY": "test-key", "ORG_OPS_KICK_FALLBACK_CLOUD": "1"},
            clear=False,
        ):
            os.environ.pop("ORG_OPS_KICK_RUNTIME", None)
            os.environ.pop("ORG_OPS_REPO_URL", None)
            attempts: list[str] = []

            def fake_attempt(prompt: str, *, cwd, label: str) -> int:
                attempts.append(label)
                return 1 if "cloud" not in label else 0

            with mock.patch.object(kick, "_attempt_kick", side_effect=fake_attempt):
                with mock.patch.object(kick, "resolve_repo_url", return_value="https://git/repo.git"):
                    code = kick.kick_prompt("planning-pm テスト", label="KICK")
        self.assertEqual(code, 0)
        self.assertEqual(attempts, ["KICK", "KICK-cloud"])

    def test_kick_prompt_no_cloud_retry_without_repo_url(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"CURSOR_API_KEY": "test-key", "ORG_OPS_KICK_FALLBACK_CLOUD": "1"},
            clear=False,
        ):
            os.environ.pop("ORG_OPS_KICK_RUNTIME", None)
            os.environ.pop("ORG_OPS_REPO_URL", None)
            with mock.patch.object(kick, "_attempt_kick", return_value=1) as attempt_mock:
                with mock.patch.object(kick, "resolve_repo_url", return_value=None):
                    code = kick.kick_prompt("x", label="KICK", hint_manual="manual")
        self.assertEqual(code, 1)
        self.assertEqual(attempt_mock.call_count, 1)

    def test_async_kick_default_on_win32(self) -> None:
        with mock.patch.object(kick.sys, "platform", "win32"):
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("ORG_OPS_KICK_ASYNC", None)
                self.assertTrue(kick._use_async_kick())

    def test_async_kick_off_on_linux(self) -> None:
        with mock.patch.object(kick.sys, "platform", "linux"):
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("ORG_OPS_KICK_ASYNC", None)
                self.assertFalse(kick._use_async_kick())

    def test_async_kick_forced_via_env(self) -> None:
        with mock.patch.object(kick.sys, "platform", "linux"):
            with mock.patch.dict(os.environ, {"ORG_OPS_KICK_ASYNC": "1"}, clear=False):
                self.assertTrue(kick._use_async_kick())

    def test_kick_in_process_uses_async_on_win32(self) -> None:
        fake_result = mock.Mock(status="completed", result="")
        with mock.patch.dict(os.environ, {"CURSOR_API_KEY": "test-key"}, clear=False):
            with mock.patch.object(kick, "_build_agent_options", return_value=object()):
                with mock.patch.object(kick, "_use_async_kick", return_value=True):
                    with mock.patch.object(
                        kick, "_run_async_prompt", return_value=fake_result
                    ) as async_mock:
                        code = kick._kick_in_process(
                            "planning-pm テスト", cwd=Path("."), label="KICK"
                        )
        self.assertEqual(code, 0)
        async_mock.assert_called_once()

    def test_isolated_subprocess_uses_utf8_decode(self) -> None:
        fake_result = CompletedProcess(
            args=[],
            returncode=0,
            stdout="KICK  日本語\n",
            stderr="",
        )
        with mock.patch.object(kick.subprocess, "run", return_value=fake_result) as run_mock:
            with mock.patch.object(kick, "_windows_creationflags", return_value=0):
                code = kick._kick_isolated_subprocess(
                    "planning-pm テスト",
                    cwd=Path("."),
                    label="KICK",
                )
        self.assertEqual(code, 0)
        kwargs = run_mock.call_args.kwargs
        self.assertEqual(kwargs.get("encoding"), "utf-8")
        self.assertEqual(kwargs.get("errors"), "replace")
        self.assertEqual(run_mock.call_args.kwargs["env"].get("PYTHONIOENCODING"), "utf-8")


if __name__ == "__main__":
    unittest.main()
