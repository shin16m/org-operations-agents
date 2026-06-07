#!/usr/bin/env python3
"""Backfill OS State on legacy Task Type=Epic tasks via syscall.init_epic.

Usage:
  python tools/backfill_epic_os_state.py --project <GID> --dry-run
  python tools/backfill_epic_os_state.py --project <GID> -y
  python tools/backfill_epic_os_state.py --epic <GID> --dry-run
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORG_OS_SRC = ROOT / "products/org-os/src"
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
for p in (str(ORG_OS_SRC), str(ASANA_OPT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from agent_handler_asana import load_env_from_dotfile  # noqa: E402
from org_os import syscall  # noqa: E402
from org_os.backfill import BackfillScan, EpicBackfillRow, scan_project  # noqa: E402
from org_os.env import load_dotenv  # noqa: E402


def _safe(text: str) -> str:
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        return text.encode(enc, errors="replace").decode(enc, errors="replace")
    except LookupError:
        return text


def _print_row(prefix: str, row: EpicBackfillRow) -> None:
    print(
        _safe(
            f"  {prefix}  {row.gid}  os_state={row.os_state or '-'}  "
            f"action={row.action}  {row.name[:50]}  ({row.reason})"
        )
    )


def _resolve_project(explicit: str | None) -> str:
    load_dotenv()
    pid = (explicit or os.getenv("ASANA_PROJECT_ID", "")).strip()
    if not pid:
        raise SystemExit("ERROR  --project or ASANA_PROJECT_ID required")
    return pid


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", default=None, help="Asana project GID")
    p.add_argument("--epic", default=None, help="Single epic GID (optional)")
    p.add_argument("--dry-run", action="store_true", help="List only; no init_epic")
    p.add_argument("--include-completed", action="store_true", help="Include completed epics")
    p.add_argument("-y", action="store_true", help="Apply without confirmation")
    args = p.parse_args()

    load_env_from_dotfile()
    project = _resolve_project(args.project)

    scan: BackfillScan = scan_project(
        project,
        epic_gid=args.epic,
        include_completed=args.include_completed,
    )

    print(f"BACKFILL  project={project}  scanned={len(scan.rows)}")
    for row in scan.rows:
        if row.action == "init":
            _print_row("INIT", row)
        elif row.action == "warn":
            _print_row("WARN", row)

    ok_n = sum(1 for r in scan.rows if r.action == "ok")
    skip_n = sum(1 for r in scan.rows if r.action == "skip")
    print(
        f"SUMMARY  init={len(scan.init_candidates)}  warn={len(scan.warnings)}  "
        f"ok={ok_n}  skip={skip_n}"
    )

    if not scan.init_candidates:
        print("NOTHING  no epics need init_epic")
        return 0

    if args.dry_run:
        print("DRY-RUN  no changes applied")
        return 0

    if not args.y:
        print(f"Apply init_epic to {len(scan.init_candidates)} epic(s)? [y/N]", file=sys.stderr)
        if input().strip().lower() not in ("y", "yes"):
            print("cancelled", file=sys.stderr)
            return 1

    for row in scan.init_candidates:
        syscall.init_epic(row.gid)
        print(f"APPLIED  init_epic  {row.gid}  -> Ready")
    return 0


if __name__ == "__main__":
    sys.exit(main())
