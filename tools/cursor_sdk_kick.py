#!/usr/bin/env python3
"""Shared Cursor SDK kick with Windows subprocess isolation.

Usage (library):
  from cursor_sdk_kick import kick_prompt
  exit_code = kick_prompt(prompt, cwd=ROOT, label="KICK")

Usage (worker child — internal):
  python tools/cursor_sdk_kick.py --worker --prompt-file /path/to/prompt.txt --cwd <repo_root>

Environment:
  ORG_OPS_KICK_RUNTIME   local | cloud | auto (default auto: cloud if ORG_OPS_REPO_URL set else local)
  ORG_OPS_KICK_ISOLATE   1 (default) | 0 — Windows subprocess isolation
  ORG_OPS_KICK_ASYNC     1 | 0 — use async SDK surface (default 1 on win32)
                          Required on Windows: the sync bridge uses select()
                          on a pipe fd → WinError 10038. The async surface
                          reads the pipe via ProactorEventLoop (IOCP).
  ORG_OPS_KICK_WORKER    1 — set in worker child; skips re-isolation
  ORG_OPS_REPO_URL       git remote URL for cloud runtime (optional; auto from origin)
  ORG_OPS_REPO_REF       branch/ref for cloud (default main)
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KICK_WORKER_ENV = "ORG_OPS_KICK_WORKER"
DEFAULT_MODEL = "composer-2.5"
SUBPROCESS_TEXT_ENCODING = "utf-8"


def _load_dotenv_if_needed() -> None:
    """Load skills/platform/asana-buddy/optional/.env (CURSOR_API_KEY, etc.)."""
    asana_opt = ROOT / "skills/platform/asana-buddy/optional"
    if str(asana_opt) not in sys.path:
        sys.path.insert(0, str(asana_opt))
    try:
        from agent_handler_asana import load_env_from_dotfile  # noqa: WPS433

        load_env_from_dotfile()
    except ImportError:
        pass


def _kick_subprocess_env(base: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(base or os.environ)
    env.setdefault("PYTHONIOENCODING", SUBPROCESS_TEXT_ENCODING)
    return env


def _configure_stdio_utf8() -> None:
    if sys.platform != "win32":
        return
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding=SUBPROCESS_TEXT_ENCODING, errors="replace")


def kick_runtime_mode() -> str:
    raw = os.environ.get("ORG_OPS_KICK_RUNTIME", "auto").strip().lower()
    if raw in ("local", "cloud"):
        return raw
    if os.environ.get("ORG_OPS_REPO_URL", "").strip():
        return "cloud"
    return "local"


def isolation_enabled() -> bool:
    if sys.platform != "win32":
        return False
    if os.environ.get(KICK_WORKER_ENV, "").strip() == "1":
        return False
    flag = os.environ.get("ORG_OPS_KICK_ISOLATE", "1").strip().lower()
    return flag not in ("0", "false", "no")


def cloud_fallback_enabled() -> bool:
    """Whether a local kick failure should retry once on cloud runtime.

    Default on for win32 (local SDK bridge is unreliable — WinError 10038),
    off elsewhere. Override with ORG_OPS_KICK_FALLBACK_CLOUD.
    """
    raw = os.environ.get("ORG_OPS_KICK_FALLBACK_CLOUD", "").strip().lower()
    if raw in ("1", "true", "yes"):
        return True
    if raw in ("0", "false", "no"):
        return False
    return sys.platform == "win32"


def resolve_repo_url() -> str | None:
    explicit = os.environ.get("ORG_OPS_REPO_URL", "").strip()
    if explicit:
        return explicit
    try:
        from win_subprocess import run as win_run  # noqa: WPS433

        r = win_run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding=SUBPROCESS_TEXT_ENCODING,
            errors="replace",
            check=False,
        )
        url = (r.stdout or "").strip()
        return url or None
    except OSError:
        return None


def _build_agent_options(*, api_key: str, cwd: Path):
    from cursor_sdk import AgentOptions, CloudAgentOptions, LocalAgentOptions  # type: ignore

    mode = kick_runtime_mode()
    if mode == "cloud":
        repo_url = resolve_repo_url()
        if not repo_url:
            raise ValueError("ORG_OPS_KICK_RUNTIME=cloud requires ORG_OPS_REPO_URL or git origin")
        ref = os.environ.get("ORG_OPS_REPO_REF", "main").strip() or "main"
        return AgentOptions(
            api_key=api_key,
            model=DEFAULT_MODEL,
            cloud=CloudAgentOptions(
                repos=[{"url": repo_url, "ref": ref}],
                skip_reviewer_request=True,
            ),
        )
    return AgentOptions(
        api_key=api_key,
        model=DEFAULT_MODEL,
        local=LocalAgentOptions(cwd=str(cwd)),
    )


def _use_async_kick() -> bool:
    """Whether to drive the kick through the async SDK surface.

    Required on Windows: the sync bridge (`cursor_sdk._bridge`) reads the
    bridge subprocess's stderr pipe with `selectors.DefaultSelector()`
    (`select()`), which on Windows only accepts sockets — a pipe fd raises
    OSError WinError 10038. The async surface reads the pipe through the
    ProactorEventLoop (IOCP/overlapped IO), avoiding `select()` entirely.
    Overridable via ORG_OPS_KICK_ASYNC (1/0).
    """
    raw = os.environ.get("ORG_OPS_KICK_ASYNC", "").strip().lower()
    if raw in ("1", "true", "yes"):
        return True
    if raw in ("0", "false", "no"):
        return False
    return sys.platform == "win32"


async def _async_prompt(prompt: str, options, *, cwd: Path):
    from cursor_sdk.asyncio import AsyncAgent, AsyncClient  # type: ignore

    from win_subprocess import patch_async_subprocess_no_window, win_bridge_command_argv  # noqa: WPS433

    bridge_cmd = win_bridge_command_argv()
    launch_kwargs: dict[str, str | list[str]] = {"workspace": str(cwd)}
    if bridge_cmd is not None:
        launch_kwargs["command"] = bridge_cmd
    with patch_async_subprocess_no_window():
        async with await AsyncClient.launch_bridge(**launch_kwargs) as client:
            return await AsyncAgent.prompt(prompt, options, client=client)


def _run_async_prompt(prompt: str, options, *, cwd: Path):
    import asyncio

    if sys.platform == "win32":
        # Proactor loop reads the bridge stderr pipe via IOCP rather than
        # select(), sidestepping the sync bridge's WinError 10038.
        policy = getattr(asyncio, "WindowsProactorEventLoopPolicy", None)
        if policy is not None and not isinstance(
            asyncio.get_event_loop_policy(), policy
        ):
            asyncio.set_event_loop_policy(policy())
    return asyncio.run(_async_prompt(prompt, options, cwd=cwd))


def _kick_in_process(prompt: str, *, cwd: Path, label: str) -> int:
    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        return -1

    options = _build_agent_options(api_key=api_key, cwd=cwd)
    if _use_async_kick():
        print(f"{label}  cursor_sdk AsyncAgent.prompt starting…")
        result = _run_async_prompt(prompt, options, cwd=cwd)
    else:
        from cursor_sdk import Agent  # type: ignore

        print(f"{label}  cursor_sdk Agent.prompt starting…")
        result = Agent.prompt(prompt, options)
    print(f"{label}  cursor_sdk status={result.status}")
    if getattr(result, "result", None):
        text = str(result.result)
        if text.strip():
            print(text[:500])
    if result.status == "error":
        return 2
    return 0


def _windows_creationflags() -> int:
    from win_subprocess import creationflags_isolated_worker  # noqa: WPS433

    return creationflags_isolated_worker()


def _kick_isolated_subprocess(prompt: str, *, cwd: Path, label: str) -> int:
    script = Path(__file__).resolve()
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".txt",
        delete=False,
    ) as fh:
        fh.write(prompt)
        prompt_path = fh.name

    env = _kick_subprocess_env()
    env[KICK_WORKER_ENV] = "1"
    cmd = [
        sys.executable,
        str(script),
        "--worker",
        "--prompt-file",
        prompt_path,
        "--cwd",
        str(cwd),
        "--label",
        label,
    ]
    print(f"{label}  isolated_subprocess  platform=win32  worker={script.name}")
    try:
        r = subprocess.run(
            cmd,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
            encoding=SUBPROCESS_TEXT_ENCODING,
            errors="replace",
            creationflags=_windows_creationflags(),
        )
    finally:
        try:
            os.unlink(prompt_path)
        except OSError:
            pass

    stdout = (r.stdout or "").strip()
    stderr = (r.stderr or "").strip()
    if stdout:
        for line in stdout.splitlines()[-15:]:
            print(line)
    if stderr:
        for line in stderr.splitlines()[-15:]:
            print(line, file=sys.stderr)
    return r.returncode


def _attempt_kick(prompt: str, *, cwd: Path, label: str) -> int:
    """Single kick attempt. Returns exit code (non-zero = failure)."""
    if isolation_enabled():
        try:
            return _kick_isolated_subprocess(prompt, cwd=cwd, label=label)
        except OSError as exc:
            print(f"{label}  FAILED  isolated_subprocess OSError={exc}", file=sys.stderr)
            return 1
    try:
        return _kick_in_process(prompt, cwd=cwd, label=label)
    except OSError as exc:
        print(f"{label}  FAILED  OSError={exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"{label}  FAILED  config={exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 — kick boundary
        print(f"{label}  FAILED  {type(exc).__name__}={exc}", file=sys.stderr)
        return 1


def kick_prompt(
    prompt: str,
    *,
    cwd: Path | None = None,
    label: str = "KICK",
    no_api_key_exit: int = 2,
    no_sdk_exit: int = 2,
    skip_no_key: str = "CURSOR_API_KEY unset — use poller --human snippet",
    skip_no_sdk: str = "cursor_sdk not installed",
    hint_manual: str | None = None,
) -> int:
    """Run Cursor SDK kick. Returns process exit code.

    On a failed local-runtime attempt, retries once on cloud runtime when
    cloud_fallback_enabled() and a repo URL is resolvable (Windows local
    bridge is unreliable — WinError 10038).
    """
    work_cwd = cwd or ROOT
    _load_dotenv_if_needed()
    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        print(f"SKIP  {skip_no_key}", file=sys.stderr)
        if hint_manual:
            print(f"HINT  {hint_manual}", file=sys.stderr)
        return no_api_key_exit

    try:
        import cursor_sdk  # noqa: F401  # type: ignore
    except ImportError:
        print(f"SKIP  {skip_no_sdk}", file=sys.stderr)
        if hint_manual:
            print(f"HINT  pip install cursor-sdk · {hint_manual}", file=sys.stderr)
        return no_sdk_exit

    code = _attempt_kick(prompt, cwd=work_cwd, label=label)

    if code != 0 and kick_runtime_mode() == "local" and cloud_fallback_enabled():
        repo_url = resolve_repo_url()
        if repo_url:
            print(
                f"{label}  fallback_cloud  local kick failed — retrying on cloud "
                f"repo={repo_url}",
                file=sys.stderr,
            )
            prev = os.environ.get("ORG_OPS_KICK_RUNTIME")
            os.environ["ORG_OPS_KICK_RUNTIME"] = "cloud"
            try:
                code = _attempt_kick(prompt, cwd=work_cwd, label=f"{label}-cloud")
            finally:
                if prev is None:
                    os.environ.pop("ORG_OPS_KICK_RUNTIME", None)
                else:
                    os.environ["ORG_OPS_KICK_RUNTIME"] = prev
        else:
            print(
                f"{label}  fallback_cloud  unavailable — no ORG_OPS_REPO_URL / git origin",
                file=sys.stderr,
            )

    if code != 0 and hint_manual:
        print(f"HINT  {hint_manual}", file=sys.stderr)
    return code


def _worker_main(args: argparse.Namespace) -> int:
    _configure_stdio_utf8()
    prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    cwd = Path(args.cwd)
    label = args.label or "KICK"
    try:
        return _kick_in_process(prompt, cwd=cwd, label=label)
    except OSError as exc:
        print(f"{label}  FAILED  OSError={exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"{label}  FAILED  config={exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"{label}  FAILED  {type(exc).__name__}={exc}", file=sys.stderr)
        return 1


def main() -> int:
    p = argparse.ArgumentParser(description="Cursor SDK kick (worker entry)")
    p.add_argument("--worker", action="store_true", help="Internal: run kick in this process")
    p.add_argument("--prompt-file", help="Prompt text file (with --worker)")
    p.add_argument("--cwd", default=str(ROOT))
    p.add_argument("--label", default="KICK")
    p.add_argument("--dry-run-isolation", action="store_true", help="Print isolation decision and exit 0")
    args = p.parse_args()

    if args.dry_run_isolation:
        print(
            f"isolation  platform={sys.platform}  "
            f"enabled={isolation_enabled()}  runtime={kick_runtime_mode()}  "
            f"worker={os.environ.get(KICK_WORKER_ENV, '')}"
        )
        return 0

    if args.worker:
        if not args.prompt_file:
            print("error: --prompt-file required with --worker", file=sys.stderr)
            return 2
        return _worker_main(args)

    print("error: use kick_prompt() from library or --worker mode", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
