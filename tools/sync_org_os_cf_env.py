#!/usr/bin/env python3
"""Discover org-os epic CF GIDs (OS State · Approval Required) and sync to .env.

Usage:
  python tools/sync_org_os_cf_env.py --project 1214771428861230 --dry-run
  python tools/sync_org_os_cf_env.py --project 1214771428861230 --write -y
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

OS_STATE_FIELD = "OS State"
APPROVAL_FIELD = "Approval Required"
APPROVAL_RESULT_FIELD = "Approval Result"
SUSPEND_REASON_FIELD = "OS Suspend Reason"
OS_STATE_ENUMS = ("Ready", "Running", "Waiting", "Done")
APPROVAL_ENUMS = ("Yes", "No")
APPROVAL_RESULT_ENUMS = ("OK", "NG")
SUSPEND_REASON_ENV = {
    "Approval": "ASANA_OS_SUSPEND_REASON_APPROVAL_GID",
    "Human Review": "ASANA_OS_SUSPEND_REASON_HUMAN_REVIEW_GID",
    "External Block": "ASANA_OS_SUSPEND_REASON_EXTERNAL_BLOCK_GID",
}


def default_env_path() -> Path:
    return ASANA_OPT / ".env"


def _fetch_fields(project_gid: str, token: str) -> dict[str, dict]:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{ASANA_BASE}/projects/{project_gid}/custom_field_settings",
        headers=headers,
        params={
            "opt_fields": "custom_field.name,custom_field.gid,custom_field.enum_options.name,custom_field.enum_options.gid"
        },
    )
    r.raise_for_status()
    out: dict[str, dict] = {}
    for row in r.json().get("data") or []:
        cf = row.get("custom_field") or {}
        name = (cf.get("name") or "").strip()
        if name in (OS_STATE_FIELD, APPROVAL_FIELD, APPROVAL_RESULT_FIELD, SUSPEND_REASON_FIELD):
            opts = {
                (o.get("name") or "").strip(): str(o.get("gid") or "")
                for o in (cf.get("enum_options") or [])
            }
            out[name] = {"field_gid": str(cf.get("gid") or ""), "options": opts}
    return out


def fetch_org_os_gids(project_gid: str, token: str) -> dict[str, str]:
    fields = _fetch_fields(project_gid, token)
    if OS_STATE_FIELD not in fields:
        raise ValueError(f"project {project_gid}: no custom field {OS_STATE_FIELD!r}")
    if APPROVAL_FIELD not in fields:
        raise ValueError(f"project {project_gid}: no custom field {APPROVAL_FIELD!r}")

    os_row = fields[OS_STATE_FIELD]
    ap_row = fields[APPROVAL_FIELD]
    updates: dict[str, str] = {
        "ASANA_OS_STATE_FIELD_GID": os_row["field_gid"],
        "ASANA_APPROVAL_REQUIRED_FIELD_GID": ap_row["field_gid"],
    }
    for enum_name in OS_STATE_ENUMS:
        gid = os_row["options"].get(enum_name)
        if not gid:
            raise ValueError(f"OS State missing enum {enum_name!r}")
        updates[f"ASANA_OS_STATE_{enum_name.upper()}_GID"] = gid
    for enum_name in APPROVAL_ENUMS:
        gid = ap_row["options"].get(enum_name)
        if not gid:
            raise ValueError(f"Approval Required missing enum {enum_name!r}")
        updates[f"ASANA_APPROVAL_REQUIRED_{enum_name.upper()}_GID"] = gid

    if APPROVAL_RESULT_FIELD in fields:
        ar_row = fields[APPROVAL_RESULT_FIELD]
        updates["ASANA_APPROVAL_RESULT_FIELD_GID"] = ar_row["field_gid"]
        for enum_name in APPROVAL_RESULT_ENUMS:
            gid = ar_row["options"].get(enum_name)
            if gid:
                updates[f"ASANA_APPROVAL_RESULT_{enum_name.upper()}_GID"] = gid
            else:
                print(
                    f"warn  Approval Result missing enum {enum_name!r} (skip)",
                    file=sys.stderr,
                )
    else:
        print(
            f"note  {APPROVAL_RESULT_FIELD}: not found (optional, skip env keys)",
            file=sys.stderr,
        )

    if SUSPEND_REASON_FIELD in fields:
        sr_row = fields[SUSPEND_REASON_FIELD]
        updates["ASANA_OS_SUSPEND_REASON_FIELD_GID"] = sr_row["field_gid"]
        for enum_label, env_key in SUSPEND_REASON_ENV.items():
            gid = sr_row["options"].get(enum_label)
            if not gid:
                for opt_name, opt_gid in sr_row["options"].items():
                    if opt_name.strip().lower() == enum_label.lower():
                        gid = opt_gid
                        break
            if gid:
                updates[env_key] = gid
            else:
                print(
                    f"warn  {SUSPEND_REASON_FIELD} missing enum {enum_label!r} (skip {env_key})",
                    file=sys.stderr,
                )
    else:
        print(
            f"note  {SUSPEND_REASON_FIELD}: not found (optional until added in Asana)",
            file=sys.stderr,
        )
    return updates


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
    p = argparse.ArgumentParser(description="Sync org-os epic CF GIDs from Asana project to .env")
    p.add_argument("--project", required=True, help="Asana project GID")
    p.add_argument("--env-file", type=Path, default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--write", action="store_true")
    p.add_argument("-y", action="store_true")
    args = p.parse_args()

    if not args.dry_run and not args.write:
        p.error("use --dry-run or --write")

    load_env_from_dotfile()
    token = get_token()
    updates = fetch_org_os_gids(args.project, token)

    print(
        f"OK  project={args.project}  fields={OS_STATE_FIELD},{APPROVAL_FIELD},"
        f"{SUSPEND_REASON_FIELD}(optional),{APPROVAL_RESULT_FIELD}(optional)"
    )
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
