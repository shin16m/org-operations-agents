"""Windows subprocess helpers — hide console windows for org-ops kick chains."""
from __future__ import annotations

import asyncio
import contextlib
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any


def creationflags_no_window() -> int:
    """CREATE_NO_WINDOW for synchronous child processes (no new console)."""
    if sys.platform != "win32":
        return 0
    flag = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return int(flag) if flag else 0


def creationflags_isolated_worker() -> int:
    """Flags for cursor_sdk_kick --worker (hidden + detached from parent console)."""
    if sys.platform != "win32":
        return 0
    flags = creationflags_no_window()
    detached = getattr(subprocess, "DETACHED_PROCESS", 0)
    if detached:
        flags |= int(detached)
    return flags


def run(*popenargs: Any, **kwargs: Any) -> subprocess.CompletedProcess[Any]:
    """subprocess.run with CREATE_NO_WINDOW on Windows when not already set."""
    if sys.platform == "win32" and "creationflags" not in kwargs:
        flags = creationflags_no_window()
        if flags:
            kwargs["creationflags"] = flags
    return subprocess.run(*popenargs, **kwargs)


def win_bridge_command_argv() -> list[str] | None:
    """Launch cursor-sdk bridge via node.exe (skip cursor-sdk-bridge.cmd → cmd.exe)."""
    if sys.platform != "win32":
        return None
    try:
        import cursor_sdk._vendor as vendor  # type: ignore[import-not-found]  # noqa: WPS433
    except ImportError:
        return None
    bridge_bin = Path(vendor.__file__).resolve().parent / "bridge" / "bin"
    node = bridge_bin / "node.exe"
    js = bridge_bin.parent / "dist" / "bin" / "cursor-sdk-bridge.js"
    if node.is_file() and js.is_file():
        return [str(node), str(js)]
    return None


@contextlib.contextmanager
def patch_async_subprocess_no_window() -> Iterator[None]:
    """Inject CREATE_NO_WINDOW into asyncio.create_subprocess_exec on Windows."""
    if sys.platform != "win32":
        yield
        return
    flags = creationflags_no_window()
    if not flags:
        yield
        return
    orig = asyncio.create_subprocess_exec

    async def patched(*args: Any, **kwargs: Any) -> asyncio.subprocess.Process:
        kwargs.setdefault("creationflags", flags)
        return await orig(*args, **kwargs)

    asyncio.create_subprocess_exec = patched  # type: ignore[assignment]
    try:
        yield
    finally:
        asyncio.create_subprocess_exec = orig  # type: ignore[assignment]
