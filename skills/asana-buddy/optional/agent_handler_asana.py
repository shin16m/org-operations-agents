#!/usr/bin/env python3
"""Minimal Asana helper: creates a task in a project and optionally moves it to a section.

Usage (example):
  python agent_handler_asana.py --project 1214771428861230 --section 1214772665399078 --name "伝票電子化" --notes "テストで伝票を電子化する"

Requires: `ASANA_TOKEN` in the process environment, or the same key in a `.env` file
discovered under the current working directory or any parent directory, or under this
script's directory and its parents (first match wins). Legacy paths under
``skills/agent-creater/`` are also checked when present. Existing environment variables
are not overwritten by `.env`.
"""
import os
import sys
import argparse
from pathlib import Path
from typing import Optional

import requests

ASANA_BASE = "https://app.asana.com/api/1.0"


def _repo_root_from_script() -> Optional[Path]:
    """Return repository root (parent of ``skills/``) when this file is under ``skills/``."""
    for parent in Path(__file__).resolve().parents:
        if parent.name == "skills" and parent.parent.is_dir():
            return parent.parent
    return None


def _legacy_dotenv_candidates() -> list[Path]:
    root = _repo_root_from_script()
    if root is None:
        return []
    skills = root / "skills"
    return [
        skills / "agent-creater" / "agents" / "asana-buddy" / "optional" / ".env",
    ]


def _find_dotenv_path() -> Optional[Path]:
    """Return the first existing .env path when walking up from cwd and from this file.

    Also checks legacy paths under ``skills/agent-creater/`` for older layouts.
    """
    seen: set[Path] = set()
    anchors = (Path.cwd(), Path(__file__).resolve().parent)
    for anchor in anchors:
        for base in [anchor, *anchor.parents]:
            resolved = base.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            candidate = resolved / ".env"
            if candidate.is_file():
                return candidate
    for legacy in _legacy_dotenv_candidates():
        if legacy.is_file():
            return legacy
    return None


def _merge_dotenv_manual(path: Path) -> None:
    """Load KEY=VALUE pairs from path into os.environ if the key is not already set."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if not key:
            continue
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        if os.environ.get(key) is None:
            os.environ[key] = val


def load_env_from_dotfile() -> None:
    """Populate os.environ from the nearest .env without overriding existing vars."""
    env_path = _find_dotenv_path()
    if env_path is None:
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        _merge_dotenv_manual(env_path)
    else:
        load_dotenv(env_path, override=False)


def get_token():
    token = os.getenv("ASANA_TOKEN")
    if not token:
        print("エラー: ASANA_TOKEN が環境変数に設定されていません。")
        sys.exit(1)
    # Ensure token is ASCII-safe for HTTP headers
    try:
        token.encode('ascii')
    except UnicodeEncodeError:
        token = token.encode('utf-8', 'ignore').decode('ascii', 'ignore')
        print("警告: ASANA_TOKEN に非ASCII文字が含まれていたため除去しました。")
    return token


def create_task(project_id, name, notes, token):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"data": {"name": name, "notes": notes, "projects": [project_id]}}
    r = requests.post(f"{ASANA_BASE}/tasks", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()["data"]


def add_task_to_section(section_id, task_gid, token):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"data": {"task": task_gid}}
    r = requests.post(f"{ASANA_BASE}/sections/{section_id}/addTask", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


def main():
    p = argparse.ArgumentParser(description="Create Asana task (minimal helper)")
    p.add_argument("--project", required=True)
    p.add_argument("--section", default=None)
    p.add_argument("--name", required=True)
    p.add_argument("--notes", default="")
    p.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip the interactive confirmation prompt (for scripts/CI).",
    )
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()

    if not args.yes:
        print("確認: Asana にタスクを作成してよいですか？ (y/N): ", end="")
        if input().strip().lower() != "y":
            print("中止します。")
            sys.exit(0)

    task = create_task(args.project, args.name, args.notes, token)

    if args.section:
        add_task_to_section(args.section, task["gid"], token)

    print("作成済み:", task.get("gid"))
    if task.get("permalink_url"):
        print("URL:", task.get("permalink_url"))


if __name__ == "__main__":
    main()
