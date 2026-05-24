#!/usr/bin/env python3
"""Discover Task Type (Intake or Epic) custom field GIDs for a project and sync to .env.

Usage:
  python tools/sync_task_type_env.py --project 1214771428861230 --dry-run
  python tools/sync_task_type_env.py --project 1214771428861230 --write -y
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
if str(ASANA_OPT) not in sys.path:
    sys.path.insert(0, str(ASANA_OPT))

import requests  # noqa: E402

from agent_handler_asana import ASANA_BASE, get_token, load_env_from_dotfile  # noqa: E402

FIELD_NAMES = ("Task Type", "Task Type (Intake or Epic)", "task type")
DISPLAY_FIELD_NAME = "Task Type"
ENV_KEYS = (
    "ASANA_TASK_TYPE_FIELD_GID",
    "ASANA_TASK_TYPE_INTAKE_GID",
    "ASANA_TASK_TYPE_EPIC_GID",
)
PROJECT_KEY = "ASANA_PROJECT_ID"


def default_env_path() -> Path:
    return ASANA_OPT / ".env"


def _match_field_name(name: str) -> bool:
    n = (name or "").strip()
    if not n:
        return False
    lower = n.lower()
    return any(n == candidate or lower == candidate.lower() for candidate in FIELD_NAMES)


def fetch_task_type_gids(project_gid: str, token: str) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{ASANA_BASE}/projects/{project_gid}/custom_field_settings",
        headers=headers,
        params={
            "opt_fields": "custom_field.name,custom_field.gid,custom_field.enum_options.name,custom_field.enum_options.gid"
        },
    )
    r.raise_for_status()
    matched_name = ""
    for row in r.json().get("data") or []:
        cf = row.get("custom_field") or {}
        cf_name = (cf.get("name") or "").strip()
        if not _match_field_name(cf_name):
            continue
        matched_name = cf_name
        field_gid = str(cf.get("gid") or "")
        intake_gid = epic_gid = ""
        for opt in cf.get("enum_options") or []:
            name = (opt.get("name") or "").strip()
            gid = str(opt.get("gid") or "")
            if name.lower() == "intake":
                intake_gid = gid
            elif name.lower() == "epic":
                epic_gid = gid
        if not field_gid or not intake_gid or not epic_gid:
            raise ValueError(
                f"project {project_gid}: {DISPLAY_FIELD_NAME!r} field found but enum Intake/Epic incomplete"
            )
        return {
            "field_gid": field_gid,
            "intake_gid": intake_gid,
            "epic_gid": epic_gid,
            "field_name": matched_name,
        }
    raise ValueError(
        f"project {project_gid}: no custom field named one of {FIELD_NAMES!r}"
    )


def read_env_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def merge_env(lines: list[str], updates: dict[str, str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    key_re = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
    for line in lines:
        m = key_re.match(line.strip())
        if m and m.group(1) in updates:
            key = m.group(1)
            out.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            out.append(line)
    for key, val in updates.items():
        if key not in seen:
            out.append(f"{key}={val}")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Sync Task Type CF GIDs from Asana project to .env")
    p.add_argument("--project", required=True, help="Asana project GID")
    p.add_argument("--env-file", type=Path, default=None, help="Target .env (default: optional/.env)")
    p.add_argument("--dry-run", action="store_true", help="Print GIDs only; do not write")
    p.add_argument("--write", action="store_true", help="Write/update .env")
    p.add_argument("-y", action="store_true", help="With --write: skip confirm")
    args = p.parse_args()

    if not args.dry_run and not args.write:
        p.error("use --dry-run or --write")

    load_env_from_dotfile()
    token = get_token()
    gids = fetch_task_type_gids(args.project, token)
    updates = {
        PROJECT_KEY: args.project,
        ENV_KEYS[0]: gids["field_gid"],
        ENV_KEYS[1]: gids["intake_gid"],
        ENV_KEYS[2]: gids["epic_gid"],
    }

    print(f"OK  project={args.project}  field={gids.get('field_name', DISPLAY_FIELD_NAME)}")
    for k, v in updates.items():
        print(f"  {k}={v}")

    if args.dry_run:
        return 0

    env_path = args.env_file or default_env_path()
    if not args.y:
        print(f"write {env_path}? [y/N]", file=sys.stderr)
        if input().strip().lower() not in ("y", "yes"):
            print("cancelled", file=sys.stderr)
            return 1

    merged = merge_env(read_env_lines(env_path), updates)
    env_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.write_text("\n".join(merged) + "\n", encoding="utf-8")
    print(f"WROTE  {env_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
