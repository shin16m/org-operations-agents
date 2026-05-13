#!/usr/bin/env python3
"""Delete an Asana task by GID (permanent). Loads ASANA_TOKEN like agent_handler_asana.

Usage:
  python asana_delete_task.py --task-gid 1234567890 -y

Requires: ASANA_TOKEN in env or nearest .env (see agent_handler_asana.load_env_from_dotfile).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_handler_asana import ASANA_BASE, get_token, load_env_from_dotfile  # noqa: E402


def delete_task(task_gid: str, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.delete(f"{ASANA_BASE}/tasks/{task_gid}", headers=headers)
    r.raise_for_status()


def main() -> None:
    p = argparse.ArgumentParser(description="Delete one Asana task by GID")
    p.add_argument("--task-gid", required=True, help="Task GID to delete")
    p.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation (required for non-interactive use)",
    )
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()

    if not args.yes:
        print("Use -y to confirm permanent delete.", file=sys.stderr)
        sys.exit(2)

    delete_task(args.task_gid.strip(), token)
    print(f"deleted task gid={args.task_gid}")


if __name__ == "__main__":
    main()
