#!/usr/bin/env python3
"""CLI auto-bootstrap: intake snapshot → bootstrap Handoff → Asana parent + planning child.

Usage:
  python tools/auto_intake_runner.py --task <GID> --dry-run
  python tools/auto_intake_runner.py --task <GID> -y
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
if str(ASANA_OPT) not in sys.path:
    sys.path.insert(0, str(ASANA_OPT))

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import console_safe  # noqa: E402

EPIC_PREFIX = "【org-ops】"
HANDOFF_DIR = ROOT / "output/planning/handoff"
INTAKE_DIR = ROOT / "output/platform/intake"
PLANNING_SUB = {
    "title": "企画・Handoff 作成",
    "department": "planning",
    "background": "auto-intake により bootstrap された企画子。issue-story-planner へ Handoff 作成を委譲する。",
    "summary": "ソース Asana タスクと snapshot を入力に AsanaBuddyHandoff を作成し、plan-reviewer → planning-pm gate へ進める。",
    "done_when": "Handoff JSON と PlanReviewResult が output/planning/ に保存され、planning-pm gate で承認後 handoff_to_asana が実行可能。",
}


def _slug(name: str) -> str:
    s = re.sub(r"[^\w\-]+", "-", name.strip())[:48].strip("-")
    return s or "intake"


def build_bootstrap_handoff(snapshot: dict) -> dict:
    gid = str(snapshot.get("task_gid") or "")
    name = (snapshot.get("name") or "intake").strip()
    url = snapshot.get("task_url") or f"https://app.asana.com/0/0/0/{gid}"
    notes = snapshot.get("notes") or ""
    comments_md = snapshot.get("comments_markdown") or ""

    epic_title = name if name.startswith(EPIC_PREFIX) else f"{EPIC_PREFIX}{name[:72]}"

    body = (
        f"## ソース Asana タスク\n\n"
        f"- GID: `{gid}`\n"
        f"- URL: {url}\n"
        f"- 名前: {name}\n\n"
        f"## notes\n\n{notes}\n"
    )
    if comments_md:
        body += f"\n## ソースコメント\n\n{comments_md}\n"
    body += "\n## 経路\n\nauto-intake CLI baseline（`auto_intake_runner.py`）\n"

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


def write_handoff(snapshot: dict, *, dry_run: bool) -> Path:
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    gid = str(snapshot.get("task_gid") or "unknown")
    path = HANDOFF_DIR / f"bootstrap.auto-intake.{gid}.json"
    data = build_bootstrap_handoff(snapshot)
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
        if line.startswith("created_parent "):
            parts = line.split()
            out["parent_gid"] = parts[1]
            if len(parts) > 2:
                out["parent_url"] = parts[2]
        elif line.startswith("created_subtask "):
            parts = line.split()
            if len(parts) >= 3:
                out["planning_child_gid"] = parts[2]
    return out


def emit_dispatch(parent_gid: str, planning_gid: str) -> None:
    snippet = (
        f"DispatchRequest（task_gid={planning_gid}, parent_gid={parent_gid}, "
        f"department=planning）で task-dispatcher → planning-pm"
    )
    print(f"DISPATCH  parent={parent_gid}  planning={planning_gid}")
    print(f"DISPATCH  snippet={console_safe(snippet)}")


def main() -> int:
    p = argparse.ArgumentParser(description="Auto-bootstrap from Asana intake source task")
    p.add_argument("--task", required=True, metavar="GID", help="Source task GID")
    p.add_argument("--dry-run", action="store_true", help="Print actions only (default without -y)")
    p.add_argument("-y", "--yes", action="store_true", help="Execute intake, write handoff, create Asana tasks")
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

    handoff_path = write_handoff(snapshot, dry_run=dry_run)
    if dry_run:
        print("AUTO_BOOTSTRAP  dry-run  complete")
        return 0

    result = run_handoff_to_asana(handoff_path, dry_run=False, yes=True)
    parent = result.get("parent_gid", "")
    planning = result.get("planning_child_gid", "")
    if parent and planning:
        emit_dispatch(parent, planning)
    print(f"AUTO_BOOTSTRAP  OK  at={datetime.now(timezone.utc).isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
