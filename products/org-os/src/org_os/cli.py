#!/usr/bin/env python3
"""org-os CLI — status · dispatch · watch."""
from __future__ import annotations

import argparse
import json
import sys
import time

from org_os import state_machine
from org_os import asana_client


def cmd_status(args: argparse.Namespace) -> int:
    info = state_machine.status_epic(args.epic)
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


def cmd_dispatch(args: argparse.Namespace) -> int:
    new_state = state_machine.dispatch_epic(args.epic, dry_run=args.dry_run)
    print(f"DISPATCH  epic={args.epic}  os_state={new_state}")
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    interval = max(5, args.interval)

    def scan_once() -> None:
        tasks = asana_client.list_project_tasks(args.project)
        ready = []
        waiting = []
        for t in tasks:
            if t.get("completed"):
                continue
            st = asana_client.read_os_state(t)
            if st == "Ready":
                ready.append(t)
            elif st == "Waiting":
                waiting.append(t)
        print(f"WATCH  project={args.project}  ready={len(ready)}  waiting={len(waiting)}")
        for t in ready[:10]:
            print(f"  READY  {t.get('gid')}  {(t.get('name') or '')[:60]}")

    scan_once()
    if args.once:
        return 0
    while True:
        time.sleep(interval)
        scan_once()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="org-os", description="Epic OS state machine")
    sub = p.add_subparsers(dest="command", required=True)

    ps = sub.add_parser("status", help="Show epic OS State + Approval Required")
    ps.add_argument("--epic", required=True)
    ps.set_defaults(func=cmd_status)

    pd = sub.add_parser("dispatch", help="Ready → Running")
    pd.add_argument("--epic", required=True)
    pd.add_argument("--dry-run", action="store_true")
    pd.set_defaults(func=cmd_dispatch)

    pw = sub.add_parser("watch", help="Poll project for Ready / Waiting epics")
    pw.add_argument("--project", required=True)
    pw.add_argument("--interval", type=int, default=60)
    pw.add_argument("--once", action="store_true")
    pw.set_defaults(func=cmd_watch)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except (RuntimeError, ValueError) as exc:
        print(f"ERROR  {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
