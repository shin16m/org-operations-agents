#!/usr/bin/env python3
"""Mark an Asana task completed (PM / worker workflow)."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parents[3]
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_comment_guard import validate_worker_sub_complete  # noqa: E402
from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    console_safe,
    fetch_task,
    is_epic_task,
    is_human_gate_task_name,
    set_task_completed,
)


def _retro_gate_hook(epic_gid: str) -> int:
    """WARN (and optionally block) before org-os complete on epics."""
    py = _REPO_ROOT / ".venv/Scripts/python.exe"
    if not py.is_file():
        py = Path(sys.executable)
    cmd = [
        str(py),
        str(_REPO_ROOT / "tools/epic_retrospective_complete_hook.py"),
        "--epic",
        epic_gid,
    ]
    return subprocess.run(cmd, cwd=str(_REPO_ROOT)).returncode


def _org_os_complete_epic(epic_gid: str, *, dry_run: bool, strict: bool) -> int:
    """Invoke org-os complete (--allow-skip unless --strict)."""
    py = _REPO_ROOT / ".venv/Scripts/python.exe"
    if not py.is_file():
        py = Path(sys.executable)
    cmd = [str(py), str(_REPO_ROOT / "tools/run_org_os.py"), "complete", "--epic", epic_gid]
    if dry_run:
        cmd.append("--dry-run")
    if not strict:
        cmd.append("--allow-skip")
    return subprocess.run(cmd, cwd=str(_REPO_ROOT)).returncode


def main() -> None:
    p = argparse.ArgumentParser(description="Set Asana task completed flag")
    p.add_argument("--gid", required=True, help="Task GID")
    p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    p.add_argument(
        "--undo",
        action="store_true",
        help="Mark incomplete (dryrun/teardown only — not for PM review rework)",
    )
    p.add_argument(
        "--allow-human-gate",
        action="store_true",
        help="Allow completing 【レビュー】/【承認】 subs (dryrun teardown only — not for agents)",
    )
    p.add_argument(
        "--strict-os",
        action="store_true",
        help="Exit non-zero if org-os complete fails on an epic (default: warn and continue)",
    )
    p.add_argument(
        "--skip-org-os",
        action="store_true",
        help="Do not call org-os complete even for epics (dryrun/teardown)",
    )
    p.add_argument(
        "--skip-worker-guards",
        action="store_true",
        help="Skip worker signed-comment / md-attach checks (dryrun teardown only)",
    )
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()
    completed = not args.undo
    task: dict | None = None

    if completed and not args.allow_human_gate:
        task = fetch_task(args.gid, token)
        if is_human_gate_task_name(task.get("name") or ""):
            print(
                f"ERROR: task {args.gid} is a human gate ({task.get('name')!r}). "
                "Only the human assignee may complete it in Asana UI. "
                "Agents must not run complete_task on 【レビュー】/【承認】 subs.",
                file=sys.stderr,
            )
            sys.exit(3)

    if completed and not args.skip_worker_guards:
        err = validate_worker_sub_complete(task_gid=args.gid, token=token)
        if err:
            print(f"ERROR: {err}", file=sys.stderr)
            sys.exit(4)

    if completed and not args.skip_org_os and is_epic_task(args.gid, token, task=task):
        retro_rc = _retro_gate_hook(args.gid)
        if retro_rc != 0:
            sys.exit(retro_rc)
        rc = _org_os_complete_epic(args.gid, dry_run=False, strict=args.strict_os)
        if rc != 0:
            sys.exit(rc)

    if not args.yes:
        verb = "完了" if completed else "未完了"
        print(console_safe(f"タスク {args.gid} を{verb}にしますか? (y/N): "), end="")
        if input().strip().lower() != "y":
            print("abort")
            sys.exit(0)

    data = set_task_completed(args.gid, completed, token)
    print("updated", data.get("gid"), "completed=", data.get("completed"))


if __name__ == "__main__":
    main()
