#!/usr/bin/env python3
"""Dispatch incomplete execution children to team PMs (L2).

Reads organizations.yaml + dispatch-prompt-ssot.md. Used by workflow-orchestrator L2 dispatch (chat-driven).

Usage:
  python tools/task_dispatcher.py --parent <EPIC_GID> --dry-run
  python tools/task_dispatcher.py --parent <EPIC_GID> --list
  python tools/task_dispatcher.py --parent <EPIC_GID> --task <CHILD_GID> --dry-run
  python tools/task_dispatcher.py --parent <EPIC_GID> --kick -y
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
ORG_OS_SRC = ROOT / "products/org-os/src"
TOOLS = ROOT / "tools"
for p in (str(ASANA_OPT), str(ORG_OS_SRC), str(TOOLS)):
    if p not in sys.path:
        sys.path.insert(0, p)

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    fetch_task,
    has_open_dependencies,
    list_subtasks,
    parse_task_assignment,
    read_execution_order,
    read_execution_order_from_notes,
)
from dispatch_prompt_util import (  # noqa: E402
    EXECUTION_DISPATCH_ORDER,
    infer_department,
    load_organizations,
    render_dispatch_prompt,
    resolve_entry_agent,
)
from cursor_sdk_kick import kick_prompt  # noqa: E402


def _epic_children(epic_gid: str, token: str) -> list[dict]:
    rows: list[dict] = []
    org = load_organizations()
    for sub in list_subtasks(epic_gid, token):
        if sub.get("completed"):
            continue
        name = str(sub.get("name") or "")
        if name.startswith(("【承認】", "【レビュー】")):
            continue
        full = fetch_task(str(sub["gid"]), token, with_custom_fields=True)
        notes = full.get("notes") or ""
        dept = infer_department(
            notes=notes,
            title=name,
            pillar_defaults=org.get("pillar_defaults"),
        )
        assignee = parse_task_assignment(notes).get("assignee")
        exec_order = read_execution_order(full)
        if exec_order is None:
            exec_order = read_execution_order_from_notes(notes)
        rows.append(
            {
                "gid": str(sub["gid"]),
                "name": name,
                "department": dept,
                "assignee": assignee,
                "execution_order": exec_order,
            }
        )
    return rows


def _sort_execution(children: list[dict]) -> list[dict]:
    order = {d: i for i, d in enumerate(EXECUTION_DISPATCH_ORDER)}

    def key(row: dict) -> tuple[int, int, str]:
        dept = row.get("department") or "zzz"
        eo = row.get("execution_order")
        eo_key = int(eo) if isinstance(eo, int) and eo > 0 else 9999
        return (order.get(dept, 99), eo_key, row.get("gid") or "")

    exec_rows = [r for r in children if r.get("department") != "planning"]
    return sorted(exec_rows, key=key)


def pick_target(
    *,
    epic_gid: str,
    token: str,
    task_gid: str | None,
    department: str | None,
) -> dict | None:
    children = _epic_children(epic_gid, token)
    if task_gid:
        for row in children:
            if row["gid"] == task_gid:
                return row
        return None
    candidates = _sort_execution(children)
    if department:
        candidates = [r for r in candidates if r.get("department") == department]
    for row in candidates:
        if has_open_dependencies(row["gid"], token):
            print(
                f"SKIP  dispatch_dependency_blocked  task={row['gid']}  "
                f"name={row.get('name', '')[:40]}"
            )
            continue
        return row
    return None


def dispatch_cursor(prompt: str) -> int:
    return kick_prompt(
        prompt,
        cwd=ROOT,
        label="KICK",
        no_api_key_exit=0,
        no_sdk_exit=0,
        skip_no_key="CURSOR_API_KEY unset — print prompt only",
        hint_manual="print prompt only",
    )


def run_dispatch(
    *,
    epic_gid: str,
    task_gid: str | None,
    department: str | None,
    dry_run: bool,
    kick: bool,
) -> int:
    load_env_from_dotfile()
    token = get_token()
    target = pick_target(
        epic_gid=epic_gid,
        token=token,
        task_gid=task_gid,
        department=department,
    )
    if target is None:
        print(f"DISPATCH  no target  parent={epic_gid}")
        return 0

    dept = target.get("department")
    if not dept:
        print(f"DISPATCH  skip  sub={target['gid']}  reason=no_department", file=sys.stderr)
        return 1

    child_gid = target["gid"]
    entry = resolve_entry_agent(dept)
    prompt = render_dispatch_prompt(
        department=dept,
        task_gid=child_gid,
        parent_gid=epic_gid,
    )
    print(
        f"DISPATCH  parent={epic_gid}  task={child_gid}  "
        f"department={dept}  entry={entry}"
    )
    print(f"--- prompt_snippet ({entry}) ---")
    print(prompt)
    print("--- end prompt_snippet ---")

    if dry_run and not kick:
        return 0
    if kick and not dry_run:
        from execution_kick_guard import execution_kick_allowed, log_blocked  # noqa: WPS433

        ok, reason = execution_kick_allowed(epic_gid, token)
        if not ok:
            log_blocked(epic_gid=epic_gid, tool="task_dispatcher", reason=reason)
            return 0
        wrapper = (
            f"あなたは {entry} スキルです（task_dispatcher kick）。\n"
            f"親エピック GID: {epic_gid}\n"
            f"担当子タスク GID: {child_gid}\n\n"
            f"{prompt}\n"
        )
        return dispatch_cursor(wrapper)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Dispatch execution child to team PM")
    p.add_argument("--parent", required=True, help="Parent epic GID")
    p.add_argument("--task", default=None, help="Specific child GID")
    p.add_argument("--department", default=None, help="Filter by department")
    p.add_argument("--list", action="store_true", help="List incomplete execution children")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--kick", action="store_true", help="Cursor SDK kick when CURSOR_API_KEY set")
    p.add_argument("-y", "--yes", action="store_true", help="With --kick: execute SDK kick")
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()

    if args.list:
        rows = _sort_execution(_epic_children(args.parent, token))
        for row in rows:
            print(
                f"{row['gid']}  dept={row.get('department') or '-'}  "
                f"{row['name'][:60]}"
            )
        return 0

    kick = args.kick and args.yes
    return run_dispatch(
        epic_gid=args.parent,
        task_gid=args.task,
        department=args.department,
        dry_run=args.dry_run and not kick,
        kick=kick,
    )


if __name__ == "__main__":
    sys.exit(main())
