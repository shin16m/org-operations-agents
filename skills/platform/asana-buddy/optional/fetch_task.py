#!/usr/bin/env python3
"""Fetch an Asana task by GID (PM / worker workflow)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import console_safe, fetch_task, list_subtasks, parse_task_assignment  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Fetch Asana task fields by GID")
    p.add_argument("--gid", required=True, help="Task GID")
    p.add_argument("--json", action="store_true", help="Output raw JSON")
    p.add_argument("--list-subtasks", action="store_true", help="List subtasks of --gid as parent")
    p.add_argument("--show-assignee", action="store_true", help="Print チーム/担当/状態 from notes")
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()

    if args.list_subtasks:
        for t in list_subtasks(args.gid, token):
            mark = "x" if t.get("completed") else " "
            print(console_safe(f"[{mark}] {t['gid']}  {t.get('name', '')[:70]}"))
        return

    data = fetch_task(args.gid, token)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    print(console_safe(f"gid: {data.get('gid')}"))
    print(console_safe(f"name: {data.get('name')}"))
    print(console_safe(f"completed: {data.get('completed')}"))
    if args.show_assignee:
        a = parse_task_assignment(data.get("notes") or "")
        print(console_safe(f"チーム: {a.get('department') or '-'}  担当: {a.get('assignee') or '-'}  状態: {a.get('status') or '-'}"))
    parent = data.get("parent") or {}
    if parent.get("gid"):
        print(console_safe(f"parent: {parent.get('gid')} {parent.get('name', '')[:50]}"))
    print(console_safe("--- notes ---"))
    print(console_safe(data.get("notes") or ""))


if __name__ == "__main__":
    main()
