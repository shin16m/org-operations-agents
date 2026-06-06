#!/usr/bin/env python3
"""Discover Agent Type (assignee type) custom field GIDs for a project and sync to .env.

The Asana field was renamed from 担当種別 to Agent Type (2026-05). Lookup tries
FIELD_NAMES in order (case-insensitive match).

Usage:
  python tools/sync_assignee_type_env.py --project 1214771428861230 --dry-run
  python tools/sync_assignee_type_env.py --project 1215102364986851 --write -y
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

FIELD_NAMES = ("Agent Type", "agent type", "担当種別")
LEGACY_FIELD_NAME = "担当種別"
DISPLAY_FIELD_NAME = "Agent Type"
ENV_KEYS = (
    "ASANA_ASSIGNEE_TYPE_FIELD_GID",
    "ASANA_ASSIGNEE_TYPE_AI_GID",
    "ASANA_ASSIGNEE_TYPE_HUMAN_GID",
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


def _name_priority(name: str) -> int:
    """Return priority index in FIELD_NAMES (lower is preferred). len(FIELD_NAMES) if no match."""
    n_lower = (name or "").strip().lower()
    for i, candidate in enumerate(FIELD_NAMES):
        if n_lower == candidate.lower():
            return i
    return len(FIELD_NAMES)


def fetch_assignee_type_gids(
    project_gid: str, token: str, *, debug: bool = False
) -> dict[str, str]:
    """Discover Agent Type CF GIDs from project custom_field_settings.

    Strategy (lazy reject for robustness against name collisions):

    1. Collect every CF whose name matches FIELD_NAMES (case-insensitive)
    2. For each candidate, require enum_options to contain BOTH "AI" and "human"
    3. If multiple complete candidates exist, prefer FIELD_NAMES order (Agent Type > 担当種別)
    4. If no complete candidate exists, raise with the observed candidate list
    5. When debug=True (e.g. dry-run), warn-print the kept/skipped candidates so
       callers can diagnose silent collisions where another field shares the name
       (this was the failure mode that motivated the rewrite — see
       docs/verification/platform/approval-flow-e2e-dryrun.md §6).
    """
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{ASANA_BASE}/projects/{project_gid}/custom_field_settings",
        headers=headers,
        params={
            "opt_fields": "custom_field.name,custom_field.gid,custom_field.enum_options.name,custom_field.enum_options.gid"
        },
    )
    r.raise_for_status()
    rows = r.json().get("data") or []
    candidates: list[dict[str, object]] = []
    for row in rows:
        cf = row.get("custom_field") or {}
        cf_name = (cf.get("name") or "").strip()
        if not _match_field_name(cf_name):
            continue
        field_gid = str(cf.get("gid") or "")
        ai_gid = human_gid = ""
        for opt in cf.get("enum_options") or []:
            opt_name = (opt.get("name") or "").strip()
            opt_gid = str(opt.get("gid") or "")
            if opt_name.upper() == "AI":
                ai_gid = opt_gid
            elif opt_name.lower() == "human":
                human_gid = opt_gid
        candidates.append(
            {
                "field_name": cf_name,
                "field_gid": field_gid,
                "ai_gid": ai_gid,
                "human_gid": human_gid,
                "complete": bool(field_gid and ai_gid and human_gid),
                "priority": _name_priority(cf_name),
            }
        )

    valid = [c for c in candidates if c["complete"]]

    if debug or not valid:
        if not candidates:
            print(
                f"  no candidate CF matched names {FIELD_NAMES!r}",
                file=sys.stderr,
            )
        else:
            for c in candidates:
                tag = "KEPT" if c["complete"] else "SKIP"
                if c["complete"]:
                    reason = "ok"
                else:
                    missing = []
                    if not c["ai_gid"]:
                        missing.append("AI")
                    if not c["human_gid"]:
                        missing.append("human")
                    reason = f"missing enum {','.join(missing)}"
                print(
                    f"  [{tag}] field={c['field_name']!r} gid={c['field_gid']} {reason}",
                    file=sys.stderr,
                )

    if not valid:
        if not candidates:
            raise ValueError(
                f"project {project_gid}: no custom field named one of {FIELD_NAMES!r}"
            )
        raise ValueError(
            f"project {project_gid}: matched {len(candidates)} field(s) named "
            f"{FIELD_NAMES!r}, but none have both AI and human enum options"
        )

    valid.sort(key=lambda c: (c["priority"], c["field_gid"]))
    chosen = valid[0]
    return {
        "field_gid": str(chosen["field_gid"]),
        "ai_gid": str(chosen["ai_gid"]),
        "human_gid": str(chosen["human_gid"]),
        "field_name": str(chosen["field_name"]),
    }


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
    p = argparse.ArgumentParser(description="Sync Agent Type CF GIDs from Asana project to .env")
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
    gids = fetch_assignee_type_gids(args.project, token, debug=args.dry_run)
    updates = {
        PROJECT_KEY: args.project,
        ENV_KEYS[0]: gids["field_gid"],
        ENV_KEYS[1]: gids["ai_gid"],
        ENV_KEYS[2]: gids["human_gid"],
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
