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


def resolve_repo_url() -> str | None:
    explicit = os.environ.get("ORG_OPS_REPO_URL", "").strip()
    if explicit:
        return explicit
    try:
        r = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
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


def _kick_in_process(prompt: str, *, cwd: Path, label: str) -> int:
    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        return -1
    from cursor_sdk import Agent  # type: ignore

    print(f"{label}  cursor_sdk Agent.prompt starting…")
    options = _build_agent_options(api_key=api_key, cwd=cwd)
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
    if sys.platform != "win32":
        return 0
    flags = 0
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        flags |= subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
    if hasattr(subprocess, "DETACHED_PROCESS"):
        flags |= subprocess.DETACHED_PROCESS  # type: ignore[attr-defined]
    return flags


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

    env = os.environ.copy()
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
    """Run Cursor SDK kick. Returns process exit code."""
    work_cwd = cwd or ROOT
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

    if isolation_enabled():
        try:
            code = _kick_isolated_subprocess(prompt, cwd=work_cwd, label=label)
        except OSError as exc:
            print(f"{label}  FAILED  isolated_subprocess OSError={exc}", file=sys.stderr)
            if hint_manual:
                print(f"HINT  {hint_manual}", file=sys.stderr)
            return 1
        if code != 0 and hint_manual:
            print(f"HINT  {hint_manual}", file=sys.stderr)
        return code

    try:
        code = _kick_in_process(prompt, cwd=work_cwd, label=label)
    except OSError as exc:
        print(f"{label}  FAILED  OSError={exc}", file=sys.stderr)
        if hint_manual:
            print(f"HINT  {hint_manual}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"{label}  FAILED  config={exc}", file=sys.stderr)
        if hint_manual:
            print(f"HINT  {hint_manual}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 — kick boundary
        print(f"{label}  FAILED  {type(exc).__name__}={exc}", file=sys.stderr)
        if hint_manual:
            print(f"HINT  {hint_manual}", file=sys.stderr)
        return 1
    return code


def _worker_main(args: argparse.Namespace) -> int:
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
