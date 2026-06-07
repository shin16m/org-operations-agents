#!/usr/bin/env python3
"""org-os CLI — status · queue · syscall · watch."""
from __future__ import annotations

import argparse
import json
import sys
import time

from org_os import doctor as doctor_mod
from org_os import queue as queue_mod
from org_os import state_machine
from org_os import syscall
from org_os.constants import SUSPEND_REASONS


def _safe(text: str) -> str:
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        return text.encode(enc, errors="replace").decode(enc, errors="replace")
    except LookupError:
        return text


def cmd_status(args: argparse.Namespace) -> int:
    info = state_machine.status_epic(args.epic)
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


def cmd_dispatch(args: argparse.Namespace) -> int:
    result = syscall.start(args.epic, args.agent, dry_run=args.dry_run)
    print(f"START  epic={args.epic}  os_state={result['os_state']}  agent={result['agent_id']}")
    return 0


def cmd_complete(args: argparse.Namespace) -> int:
    try:
        result = syscall.complete(args.epic, dry_run=args.dry_run)
        print(f"COMPLETE  epic={args.epic}  os_state={result['os_state']}")
        return 0
    except (RuntimeError, ValueError) as exc:
        if args.allow_skip:
            print(f"WARN  complete skipped  epic={args.epic}  reason={exc}", file=sys.stderr)
            return 0
        print(f"ERROR  {exc}", file=sys.stderr)
        return 1


def _print_queue(rows: list[dict], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    for row in rows:
        print(
            f"  {row.get('epic_gid')}  {_safe((row.get('name') or '')[:60])}  "
            f"reason={row.get('suspend_reason') or '-'}"
        )


def cmd_queue_ready(args: argparse.Namespace) -> int:
    rows = queue_mod.ready_queue(args.project)
    print(f"QUEUE  kind=ready  project={args.project}  count={len(rows)}")
    _print_queue(rows, as_json=args.json)
    return 0


def cmd_queue_wait(args: argparse.Namespace) -> int:
    rows = queue_mod.wait_list(args.project)
    print(f"QUEUE  kind=wait  project={args.project}  count={len(rows)}")
    _print_queue(rows, as_json=args.json)
    return 0


def cmd_syscall_start(args: argparse.Namespace) -> int:
    result = syscall.start(args.epic, args.agent, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False))
    return 0


def cmd_syscall_suspend(args: argparse.Namespace) -> int:
    result = syscall.suspend(args.epic, args.reason, ref=args.ref, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False))
    return 0


def cmd_syscall_resume(args: argparse.Namespace) -> int:
    result = syscall.resume(args.epic, ref=args.ref, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False))
    return 0


def cmd_syscall_complete(args: argparse.Namespace) -> int:
    result = syscall.complete(args.epic, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    if args.online:
        return doctor_mod.doctor_online()
    return doctor_mod.doctor_local()


def cmd_watch(args: argparse.Namespace) -> int:
    interval = max(5, args.interval)

    def scan_once() -> None:
        ready = queue_mod.ready_queue(args.project)
        waiting = queue_mod.wait_list(args.project)
        print(
            f"WATCH  project={args.project}  ready={len(ready)}  waiting={len(waiting)}"
            f"  filter=AgentType:AI+TaskType:Epic"
        )
        for row in ready[:10]:
            print(f"  READY  {row['epic_gid']}  {_safe((row.get('name') or '')[:60])}")
        for row in waiting[:10]:
            reason = row.get("suspend_reason") or "-"
            print(
                f"  WAITING  {row['epic_gid']}  {_safe((row.get('name') or '')[:60])}  reason={reason}"
            )

    scan_once()
    if args.once:
        return 0
    while True:
        time.sleep(interval)
        scan_once()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="org-os", description="Epic OS kernel")
    sub = p.add_subparsers(dest="command", required=True)

    ps = sub.add_parser("status", help="Show epic OS State snapshot")
    ps.add_argument("--epic", required=True)
    ps.set_defaults(func=cmd_status)

    pd = sub.add_parser("dispatch", help="Alias for syscall start (Ready → Running)")
    pd.add_argument("--epic", required=True)
    pd.add_argument("--agent", default=None, help="Override ORG_OS_AGENT_ID")
    pd.add_argument("--dry-run", action="store_true")
    pd.set_defaults(func=cmd_dispatch)

    pc = sub.add_parser("complete", help="Ready/Running/Waiting → Done")
    pc.add_argument("--epic", required=True)
    pc.add_argument("--dry-run", action="store_true")
    pc.add_argument("--allow-skip", action="store_true")
    pc.set_defaults(func=cmd_complete)

    pq = sub.add_parser("queue", help="Read-only epic queues")
    pq_sub = pq.add_subparsers(dest="queue_kind", required=True)
    pqr = pq_sub.add_parser("ready", help="Ready queue (FIFO)")
    pqr.add_argument("--project", required=True)
    pqr.add_argument("--json", action="store_true")
    pqr.set_defaults(func=cmd_queue_ready)
    pqw = pq_sub.add_parser("wait", help="Waiting list")
    pqw.add_argument("--project", required=True)
    pqw.add_argument("--json", action="store_true")
    pqw.set_defaults(func=cmd_queue_wait)

    psy = sub.add_parser("syscall", help="State transition syscalls")
    psy_sub = psy.add_subparsers(dest="syscall_op", required=True)
    psy_start = psy_sub.add_parser("start", help="Ready → Running")
    psy_start.add_argument("--epic", required=True)
    psy_start.add_argument("--agent", default=None)
    psy_start.add_argument("--dry-run", action="store_true")
    psy_start.set_defaults(func=cmd_syscall_start)
    psy_suspend = psy_sub.add_parser("suspend", help="Ready/Running → Waiting")
    psy_suspend.add_argument("--epic", required=True)
    psy_suspend.add_argument("--reason", required=True, choices=SUSPEND_REASONS)
    psy_suspend.add_argument("--ref", default=None)
    psy_suspend.add_argument("--dry-run", action="store_true")
    psy_suspend.set_defaults(func=cmd_syscall_suspend)
    psy_resume = psy_sub.add_parser("resume", help="Waiting → Ready")
    psy_resume.add_argument("--epic", required=True)
    psy_resume.add_argument("--ref", default=None)
    psy_resume.add_argument("--dry-run", action="store_true")
    psy_resume.set_defaults(func=cmd_syscall_resume)
    psy_complete = psy_sub.add_parser("complete", help="→ Done")
    psy_complete.add_argument("--epic", required=True)
    psy_complete.add_argument("--dry-run", action="store_true")
    psy_complete.set_defaults(func=cmd_syscall_complete)

    pdoc = sub.add_parser("doctor", help="Validate org-os env setup (local keys)")
    pdoc.add_argument(
        "--online",
        action="store_true",
        help="Also verify Asana project + CF enum names (A1-3)",
    )
    pdoc.set_defaults(func=cmd_doctor)

    pw = sub.add_parser("watch", help="Poll project queues (human-readable)")
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
