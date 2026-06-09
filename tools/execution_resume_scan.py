#!/usr/bin/env python3
"""Scan Running epics and detect execution L3b resume actions (Phase B).

Usage:
  python tools/execution_resume_scan.py --project <PROJECT_GID> --dry-run
  python tools/execution_resume_scan.py --project <PROJECT_GID> --epic <EPIC_GID> --json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
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
    console_safe,
    fetch_task,
    list_subtasks,
    parse_task_assignment,
)
from dispatch_prompt_util import infer_department, load_organizations  # noqa: E402
from org_os import asana_client  # noqa: E402
from org_os.queue import list_project_tasks  # noqa: E402
from agent_comment_guard import has_agent_comment  # noqa: E402
from pm_emit_worker_prompt import DEPT_PM, _run_fetch_assignee  # noqa: E402
from task_dispatcher import _epic_children, _sort_execution  # noqa: E402

REVIEW_MARKER = "【レビュー】"
APPROVAL_MARKER = "【承認】"
_KICKABLE_STATES = frozenset(
    {"needs_pm_kick", "needs_next_dept", "needs_worker_kick", "needs_pm_complete"}
)


@dataclass(frozen=True)
class ExecutionKickResult:
    blocked_count: int
    kicks: int
    deferred: bool
    inflight: bool
    no_progress: bool = False
    stuck_level: str | None = None


def _resolve_project(arg_project: str | None) -> str | None:
    if arg_project:
        return arg_project
    for key in ("ASANA_PROJECT_ID", "ASANA_PROJECT_GID", "ASANA_PROJECT"):
        val = os.getenv(key, "").strip()
        if val:
            return val
    return None


def running_queue(project_gid: str, *, token: str) -> list[dict]:
    rows: list[dict] = []
    for task in list_project_tasks(project_gid, token=token):
        if not asana_client.is_watch_epic(task):
            continue
        if asana_client.read_os_state(task) != "Running":
            continue
        rows.append(
            {
                "epic_gid": str(task.get("gid") or ""),
                "name": task.get("name") or "",
                "created_at": task.get("created_at"),
            }
        )
    rows.sort(key=lambda r: r.get("created_at") or "")
    return rows


def _is_gate_name(name: str) -> bool:
    n = (name or "").strip()
    return n.startswith((REVIEW_MARKER, APPROVAL_MARKER))


def _worker_subs(pm_child_gid: str, department: str, token: str) -> list[dict]:
    pm_slug = DEPT_PM.get(department, "")
    rows: list[dict] = []
    for sub in list_subtasks(pm_child_gid, token):
        if sub.get("completed"):
            continue
        name = str(sub.get("name") or "")
        if _is_gate_name(name):
            continue
        gid = str(sub["gid"])
        assignee = _run_fetch_assignee(gid) or parse_task_assignment(
            str(fetch_task(gid, token).get("notes") or "")
        ).get("assignee")
        if not assignee or assignee == pm_slug:
            continue
        rows.append({"gid": gid, "name": name, "assignee": assignee})
    return rows


from pm_review_gate_util import find_pm_assign_review_gate_sub  # noqa: E402


def _find_review_sub(pm_child_gid: str, token: str) -> dict | None:
    return find_pm_assign_review_gate_sub(pm_child_gid, token)


def classify_pm_child(
    *,
    epic_gid: str,
    pm_child: dict,
    token: str,
) -> dict:
    pm_gid = str(pm_child["gid"])
    dept = pm_child.get("department") or infer_department(
        notes=str(fetch_task(pm_gid, token).get("notes") or ""),
        title=str(pm_child.get("name") or ""),
        pillar_defaults=load_organizations().get("pillar_defaults"),
    )
    review = _find_review_sub(pm_gid, token)
    workers = _worker_subs(pm_gid, dept or "development", token)

    if not workers:
        reason = "no_worker_subs"
        hint = None
        if dept == "development":
            reason = "pm_assign_lite_required"
            hint = (
                "python skills/platform/asana-buddy/optional/pm_assign_subtasks.py "
                f"--parent {pm_gid} --plan skills/development/examples/assign-plan.lite-v1.json "
                "--department development --update-parent-assignee product-manager -y"
            )
        out = {
            "state": "needs_pm_kick",
            "epic_gid": epic_gid,
            "pm_child_gid": pm_gid,
            "department": dept,
            "reason": reason,
        }
        if hint:
            out["pm_assign_hint"] = hint
        return out

    if review and not review.get("completed"):
        return {
            "state": "wait_pm_review",
            "epic_gid": epic_gid,
            "pm_child_gid": pm_gid,
            "department": dept,
            "review_sub_gid": str(review.get("gid") or ""),
            "reason": "pm_review_gate_open",
        }

    from worker_kick_inflight import is_worker_kick_inflight, release_worker_kick  # noqa: WPS433

    for worker in workers:
        gid = worker["gid"]
        assignee = worker["assignee"]
        if has_agent_comment(gid, assignee, token):
            release_worker_kick(gid)
            return {
                "state": "needs_pm_complete",
                "epic_gid": epic_gid,
                "pm_child_gid": pm_gid,
                "department": dept,
                "worker_sub_gid": gid,
                "worker_slug": assignee,
                "worker_name": worker["name"],
                "reason": "worker_comment_without_complete",
            }
        if is_worker_kick_inflight(gid):
            return {
                "state": "wait_worker_inflight",
                "epic_gid": epic_gid,
                "pm_child_gid": pm_gid,
                "department": dept,
                "worker_sub_gid": gid,
                "worker_slug": assignee,
                "worker_name": worker["name"],
                "reason": "worker_kick_inflight",
            }
        return {
            "state": "needs_worker_kick",
            "epic_gid": epic_gid,
            "pm_child_gid": pm_gid,
            "department": dept,
            "worker_sub_gid": gid,
            "worker_slug": assignee,
            "worker_name": worker["name"],
            "reason": "incomplete_worker_without_comment",
        }

    return {
        "state": "idle",
        "epic_gid": epic_gid,
        "pm_child_gid": pm_gid,
        "department": dept,
        "reason": "all_workers_complete",
    }


def classify_running_epic(epic_gid: str, *, token: str) -> dict:
    children = _sort_execution(_epic_children(epic_gid, token))
    if not children:
        return {"state": "idle", "epic_gid": epic_gid, "reason": "all_execution_complete"}

    return classify_pm_child(epic_gid=epic_gid, pm_child=children[0], token=token)


def scan_running_actions(
    project_gid: str,
    *,
    token: str | None = None,
    epic_gid: str | None = None,
) -> list[dict]:
    load_env_from_dotfile()
    tok = token or get_token()
    epics = running_queue(project_gid, token=tok)
    if epic_gid:
        epics = [r for r in epics if r["epic_gid"] == epic_gid]
    actions: list[dict] = []
    for row in epics:
        item = classify_running_epic(row["epic_gid"], token=tok)
        item["epic_name"] = row.get("name")
        actions.append(item)
    return actions


def print_execution_scan(project_gid: str, actions: list[dict], *, dry_run: bool) -> None:
    print(console_safe(f"EXECUTION_SCAN  project={project_gid}  dry_run={dry_run}  total={len(actions)}"))
    for item in actions:
        state = item.get("state") or "?"
        epic = item.get("epic_gid") or "?"
        pm = item.get("pm_child_gid") or "-"
        dept = item.get("department") or "-"
        worker = item.get("worker_sub_gid") or "-"
        print(
            console_safe(
                f"EXECUTION  epic={epic}  state={state}  pm_child={pm}  "
                f"dept={dept}  worker={worker}  reason={item.get('reason') or '-'}"
            )
        )
    print(console_safe(f"EXECUTION_DONE  running_total={len(actions)}"))


def _max_kicks_per_cycle() -> int:
    raw = os.environ.get("ORG_OPS_MAX_WORKER_KICKS_PER_CYCLE", "3").strip()
    try:
        return max(0, int(raw))
    except ValueError:
        return 1


def _action_fingerprint(item: dict) -> tuple[str, str, str, str, str]:
    return (
        str(item.get("epic_gid") or ""),
        str(item.get("state") or ""),
        str(item.get("reason") or ""),
        str(item.get("pm_child_gid") or ""),
        str(item.get("worker_sub_gid") or ""),
    )


def _collect_project_actions(
    project_gids: list[str],
    *,
    token: str,
    dry_run: bool,
    log_scan: bool = True,
    tick_stuck: bool = True,
) -> list[dict]:
    rows: list[dict] = []
    for project_gid in project_gids:
        actions = scan_running_actions(project_gid, token=token)
        if log_scan:
            print_execution_scan(project_gid, actions, dry_run=dry_run)
        for item in actions:
            epic = str(item.get("epic_gid") or "")
            if epic and tick_stuck:
                from execution_stuck_escalate import check_and_emit_stuck  # noqa: WPS433

                check_and_emit_stuck(epic, item, token=token, dry_run=dry_run)
            rows.append(item)
    return rows


def _find_kickable_action(actions: list[dict]) -> dict | None:
    for item in actions:
        if item.get("state") in _KICKABLE_STATES:
            return item
    return None


def _has_inflight(actions: list[dict]) -> bool:
    return any(item.get("state") == "wait_worker_inflight" for item in actions)


def _kick_cmd_for_action(item: dict) -> list[str] | None:
    state = item.get("state")
    epic = str(item.get("epic_gid") or "")
    pm = str(item.get("pm_child_gid") or "")
    dept = str(item.get("department") or "development")
    worker = str(item.get("worker_sub_gid") or "")

    py = sys.executable
    if state in ("needs_pm_kick", "needs_next_dept"):
        return [py, str(TOOLS / "task_dispatcher.py"), "--parent", epic, "--kick", "-y"]
    if state == "needs_worker_kick":
        return [
            py,
            str(TOOLS / "cursor_worker_dispatch.py"),
            "--parent",
            pm,
            "--department",
            dept,
            "-y",
        ]
    if state == "needs_pm_complete":
        return [
            py,
            str(TOOLS / "pm_worker_complete_bridge.py"),
            "--parent",
            pm,
            "--sub",
            worker,
            "--department",
            dept,
            "-y",
        ]
    return None


def kick_execution_action(
    item: dict,
    *,
    execute: bool,
    dry_run: bool,
    token: str | None = None,
    blocked_out: list[dict] | None = None,
) -> int:
    cmd = _kick_cmd_for_action(item)
    if cmd is None:
        return 0
    state = item.get("state") or "?"
    epic = item.get("epic_gid") or "?"
    if execute and not dry_run and epic:
        from execution_kick_guard import execution_kick_allowed, log_blocked, worker_kick_allowed  # noqa: WPS433

        load_env_from_dotfile()
        tok = token or get_token()
        ok, reason = execution_kick_allowed(str(epic), tok)
        if not ok:
            row = {
                "epic_gid": str(epic),
                "state": state,
                "reason": reason,
                "tool": "execution_resume_scan",
            }
            log_blocked(epic_gid=str(epic), tool="execution_resume_scan", reason=reason)
            print(
                console_safe(
                    f"RUNNER  BLOCKED  epic={epic}  state={state}  reason={reason}"
                )
            )
            if blocked_out is not None:
                blocked_out.append(row)
            return 0
        if state == "needs_worker_kick" and pm:
            wok, wreason = worker_kick_allowed(str(pm), tok)
            if not wok:
                log_blocked(epic_gid=str(epic), tool="execution_resume_scan", reason=wreason)
                print(
                    console_safe(
                        f"RUNNER  BLOCKED  epic={epic}  state={state}  reason={wreason}"
                    )
                )
                if blocked_out is not None:
                    blocked_out.append(
                        {
                            "epic_gid": str(epic),
                            "state": state,
                            "reason": wreason,
                            "tool": "execution_resume_scan",
                        }
                    )
                return 0
    if not execute or dry_run:
        print(f"HINT  execution_kick  epic={epic}  state={state}  cmd={' '.join(cmd)}")
        return 0
    print(f"KICK  execution  epic={epic}  state={state}")
    from win_subprocess import run as win_run  # noqa: WPS433

    r = win_run(cmd, cwd=str(ROOT), env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    print(f"KICK  execution  epic={epic}  exit={r.returncode}")
    return r.returncode


def scan_execution_and_kick(
    *,
    project_gids: list[str],
    token: str,
    dry_run: bool,
    cursor_kick: bool,
) -> ExecutionKickResult:
    from execution_kick_guard import auto_kick_enabled  # noqa: WPS433

    auto_kick = auto_kick_enabled(cursor_kick)
    max_kicks = _max_kicks_per_cycle()
    kicks = 0
    deferred = False
    blocked_rows: list[dict] = []

    while True:
        actions = _collect_project_actions(project_gids, token=token, dry_run=dry_run)
        candidate = _find_kickable_action(actions)
        if candidate is None:
            return ExecutionKickResult(
                blocked_count=len(blocked_rows),
                kicks=kicks,
                deferred=False,
                inflight=_has_inflight(actions),
            )
        if kicks >= max_kicks:
            deferred = True
            print(f"EXECUTION  defer  reason=max_kicks_per_cycle={max_kicks}")
            return ExecutionKickResult(
                blocked_count=len(blocked_rows),
                kicks=kicks,
                deferred=True,
                inflight=_has_inflight(actions),
            )
        fp_before = _action_fingerprint(candidate)
        kick_execution_action(
            candidate,
            execute=auto_kick,
            dry_run=dry_run,
            token=token,
            blocked_out=blocked_rows,
        )
        if not auto_kick or dry_run:
            return ExecutionKickResult(
                blocked_count=len(blocked_rows),
                kicks=kicks,
                deferred=False,
                inflight=_has_inflight(actions),
            )
        kicks += 1
        actions_after = _collect_project_actions(
            project_gids,
            token=token,
            dry_run=dry_run,
            log_scan=False,
            tick_stuck=False,
        )
        candidate_after = _find_kickable_action(actions_after)
        if candidate_after and _action_fingerprint(candidate_after) == fp_before:
            epic = fp_before[0]
            state = fp_before[1]
            reason = fp_before[2]
            print(
                console_safe(
                    f"EXECUTION  no_progress  epic={epic}  state={state}  reason={reason}"
                )
            )
            from execution_stuck_escalate import check_and_emit_stuck  # noqa: WPS433

            stuck_level = check_and_emit_stuck(
                epic,
                candidate_after,
                token=token,
                dry_run=dry_run,
            )
            return ExecutionKickResult(
                blocked_count=len(blocked_rows),
                kicks=kicks,
                deferred=False,
                inflight=_has_inflight(actions_after),
                no_progress=True,
                stuck_level=stuck_level,
            )


def main() -> int:
    p = argparse.ArgumentParser(description="Scan Running epics for execution L3b actions")
    p.add_argument("--project", default=None)
    p.add_argument("--epic", default=None, help="Filter to one epic GID")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    load_env_from_dotfile()
    project = _resolve_project(args.project)
    if not project:
        print("error: --project not provided and ASANA_PROJECT_ID unset", file=sys.stderr)
        return 2

    actions = scan_running_actions(project, epic_gid=args.epic)
    if args.json:
        print(json.dumps(actions, ensure_ascii=False, indent=2))
    else:
        print_execution_scan(project, actions, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
