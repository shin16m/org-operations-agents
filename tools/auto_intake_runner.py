#!/usr/bin/env python3
"""CLI auto-bootstrap: intake snapshot → triage → bootstrap Handoff → Asana parent + planning child.

Usage:
  python tools/auto_intake_runner.py --task <GID> --dry-run
  python tools/auto_intake_runner.py --task <GID> -y
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
for p in (str(TOOLS), str(ASANA_OPT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import console_safe  # noqa: E402
from intake_triage import (  # noqa: E402
    bootstrap_notes_from_epic_input,
    epic_title_from_input,
    triage_snapshot,
)

HANDOFF_DIR = ROOT / "output/planning/handoff"
INTAKE_DIR = ROOT / "output/platform/intake"
TRIAGE_DIR = ROOT / "output/platform/triage"
PLANNING_SUB = {
    "title": "企画・Handoff 作成",
    "department": "planning",
    "background": "auto-intake により bootstrap された企画子。issue-story-planner へ Handoff 作成を委譲する。",
    "summary": "ソース Asana タスクと snapshot を入力に AsanaBuddyHandoff を作成し、plan-reviewer → planning-pm gate へ進める。",
    "done_when": "Handoff JSON と PlanReviewResult が output/planning/ に保存され、planning-pm gate で承認後 handoff_to_asana が実行可能。",
}


def build_bootstrap_handoff(snapshot: dict, epic_input: dict) -> dict:
    gid = str(snapshot.get("task_gid") or epic_input.get("metadata", {}).get("source_task_gid") or "")
    epic_title = epic_title_from_input(epic_input)
    body = bootstrap_notes_from_epic_input(epic_input, snapshot)

    return {
        "schema_version": "1.2",
        "meta": {
            "title": f"auto-intake {gid}",
            "locale": "ja-JP",
            "source_task_gid": gid,
        },
        "epic": {"title": epic_title, "notes_markdown": body},
        "subtasks": [PLANNING_SUB],
    }


def run_intake_snapshot(task_gid: str, *, dry_run: bool) -> Path:
    INTAKE_DIR.mkdir(parents=True, exist_ok=True)
    out = INTAKE_DIR / f"{task_gid}-snapshot.json"
    cmd = [
        sys.executable,
        str(ROOT / "tools/intake_from_asana.py"),
        "--task",
        task_gid,
        "--out",
        str(out),
    ]
    if dry_run:
        print(f"INTAKE  source={task_gid}  dry-run  would_run={' '.join(cmd)}")
        return out
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print(r.stderr or r.stdout, file=sys.stderr)
        raise SystemExit(r.returncode)
    print(f"INTAKE  source={task_gid}  OK  snapshot={out.as_posix()}")
    return out


def run_triage(snapshot: dict, *, dry_run: bool) -> tuple[dict, Path]:
    gid = str(snapshot.get("task_gid") or "unknown")
    out = TRIAGE_DIR / f"{gid}-epic-input.json"
    if dry_run:
        print(f"TRIAGE  source={gid}  dry-run  would_write={out.as_posix()}")
        return triage_snapshot(snapshot), out
    TRIAGE_DIR.mkdir(parents=True, exist_ok=True)
    result = triage_snapshot(snapshot)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    ei = result["epic_input"]
    print(f"TRIAGE  source={gid}  OK  out={out.as_posix()}")
    print(f"  title={ei['title'][:60]!r}  skill_tags={ei['skill_tags']}")
    return ei, out


def write_handoff(snapshot: dict, epic_input: dict, *, dry_run: bool) -> Path:
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    gid = str(snapshot.get("task_gid") or "unknown")
    path = HANDOFF_DIR / f"bootstrap.auto-intake.{gid}.json"
    data = build_bootstrap_handoff(snapshot, epic_input)
    if dry_run:
        print(f"HANDOFF  path={path.as_posix()}  dry-run")
        return path
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"HANDOFF  path={path.as_posix()}")
    return path


def run_handoff_to_asana(handoff_path: Path, *, dry_run: bool, yes: bool) -> dict[str, str]:
    cmd = [
        sys.executable,
        str(ASANA_OPT / "handoff_to_asana.py"),
        "--handoff",
        str(handoff_path),
    ]
    if dry_run:
        cmd.append("--dry-run")
    if yes and not dry_run:
        cmd.append("-y")
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
    if r.stdout:
        print(r.stdout.strip())
    if r.returncode != 0:
        if r.stderr:
            print(r.stderr.strip(), file=sys.stderr)
        raise SystemExit(r.returncode)
    out: dict[str, str] = {}
    for line in (r.stdout or "").splitlines():
        if line.startswith(("created_parent ", "synced_existing ", "updated_parent ")):
            parts = line.split()
            if len(parts) >= 2:
                out["parent_gid"] = parts[1]
            if len(parts) > 2 and line.startswith("created_parent "):
                out["parent_url"] = parts[2]
        elif line.startswith("created_subtask "):
            parts = line.split()
            if len(parts) >= 3:
                out["planning_child_gid"] = parts[2]
    return out


def run_close_intake_source(source_gid: str, epic_gid: str, *, dry_run: bool, yes: bool) -> None:
    cmd = [
        sys.executable,
        str(ASANA_OPT / "close_intake_source_task.py"),
        "--source",
        source_gid,
        "--epic",
        epic_gid,
    ]
    if dry_run:
        cmd.append("--dry-run")
    elif yes:
        cmd.append("-y")
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
    if r.stdout:
        print(r.stdout.strip())
    if r.returncode != 0:
        if r.stderr:
            print(r.stderr.strip(), file=sys.stderr)
        print(
            f"WARN  close_intake_source failed  source={source_gid}  epic={epic_gid}",
            file=sys.stderr,
        )
        raise SystemExit(r.returncode)


def emit_dispatch(parent_gid: str, planning_gid: str) -> None:
    snippet = (
        f"DispatchRequest（task_gid={planning_gid}, parent_gid={parent_gid}, "
        f"department=planning）で task-dispatcher → planning-pm"
    )
    print(f"DISPATCH  parent={parent_gid}  planning={planning_gid}")
    print(f"DISPATCH  snippet={console_safe(snippet)}")
    print(
        "DISPATCH  hint=planning gate 到達後: "
        "asana_ops_poller --record-wait <親GID> <【承認】サブGID> <URL>",
        file=sys.stderr,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Auto-bootstrap from Asana intake source task")
    p.add_argument("--task", required=True, metavar="GID", help="Source task GID")
    p.add_argument("--dry-run", action="store_true", help="Print actions only (default without -y)")
    p.add_argument("-y", "--yes", action="store_true", help="Execute intake, triage, write handoff, create Asana tasks")
    args = p.parse_args()

    dry_run = args.dry_run or not args.yes
    load_env_from_dotfile()
    get_token()  # fail early if missing

    snapshot_path = run_intake_snapshot(args.task, dry_run=dry_run)
    if dry_run:
        snapshot = {
            "task_gid": args.task,
            "task_url": f"https://app.asana.com/0/0/0/{args.task}",
            "name": "(dry-run)",
            "notes": "",
        }
    else:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))

    if dry_run:
        run_triage(snapshot, dry_run=True)
        epic_input = triage_snapshot(snapshot)["epic_input"]
    else:
        epic_input, _ = run_triage(snapshot, dry_run=False)

    handoff_path = write_handoff(snapshot, epic_input, dry_run=dry_run)
    if dry_run:
        print("AUTO_BOOTSTRAP  dry-run  complete  path=intake→triage→bootstrap")
        return 0

    source_gid = str(snapshot.get("task_gid") or args.task)
    result = run_handoff_to_asana(handoff_path, dry_run=False, yes=True)
    parent = result.get("parent_gid", "")
    planning = result.get("planning_child_gid", "")
    if parent and source_gid:
        run_close_intake_source(source_gid, parent, dry_run=False, yes=True)
    if parent and planning:
        emit_dispatch(parent, planning)
    print(
        "AUTO_BOOTSTRAP  NOTE  bootstrap only — no 【承認】 yet. "
        "Next: PLANNING_DISPATCH / planning-pm → Handoff → plan-review → create_approval_subtask",
        file=sys.stderr,
    )
    print(f"AUTO_BOOTSTRAP  OK  at={datetime.now(timezone.utc).isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
