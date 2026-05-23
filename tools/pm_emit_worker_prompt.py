#!/usr/bin/env python3
"""Emit WorkerDispatchSnippet for incomplete PM subtasks (L3b).

Usage:
  python tools/pm_emit_worker_prompt.py --parent <GID> --department development
  python tools/pm_emit_worker_prompt.py --parent <GID> --department ux --all
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA = ROOT / "skills/platform/asana-buddy/optional"
PY = ROOT / ".venv/Scripts/python.exe"
if not PY.is_file():
    PY = Path(sys.executable)

DEPT_PM = {
    "ux": "ux-pm",
    "development": "product-manager",
    "analysis": "analytics-pm",
}


def _run_fetch_list(parent: str) -> list[tuple[str, str, bool]]:
    import subprocess

    r = subprocess.run(
        [str(PY), str(ASANA / "fetch_task.py"), "--gid", parent, "--list-subtasks"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**dict(__import__("os").environ), "PYTHONIOENCODING": "utf-8"},
    )
    if r.returncode != 0:
        print(r.stderr or r.stdout, file=sys.stderr)
        sys.exit(1)
    out: list[tuple[str, str, bool]] = []
    for line in r.stdout.splitlines():
        m = re.match(r"\[([ x])\]\s+(\d+)\s+(.+)$", line.strip())
        if m:
            out.append((m.group(2), m.group(3).strip(), m.group(1) == "x"))
    return out


def _run_fetch_assignee(gid: str) -> str | None:
    import subprocess

    r = subprocess.run(
        [str(PY), str(ASANA / "fetch_task.py"), "--gid", gid, "--show-assignee"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**dict(__import__("os").environ), "PYTHONIOENCODING": "utf-8"},
    )
    if r.returncode != 0:
        return None
    m = re.search(r"担当:\s*(\S+)", r.stdout)
    return m.group(1) if m else None


def emit_snippet(
    *,
    department: str,
    parent_gid: str,
    sub_gid: str,
    worker_slug: str,
) -> str:
    return f"""【WorkerDispatch】department={department} parent={parent_gid} sub={sub_gid} worker={worker_slug}

あなたは {worker_slug} スキルです。Asana サブタスク GID {sub_gid} のみを実行してください。

1. fetch_task.py --gid {sub_gid} --show-assignee で 担当: {worker_slug} を確認（不一致なら PM へ）
2. サブ notes の done_when に従い成果物を作成
3. comment_task.py --agent {worker_slug} --skill skills/{department}/{worker_slug}/SKILL.md -y
4. PM へ完了報告（PM が complete_task.py --gid {sub_gid} -y）

親タスク {parent_gid} の workflow 全体・他サブタスクは実行しないこと。
"""


def main() -> int:
    p = argparse.ArgumentParser(description="Emit WorkerDispatchSnippet for PM subtasks")
    p.add_argument("--parent", required=True, help="PM parent child task GID")
    p.add_argument("--department", required=True, choices=sorted(DEPT_PM))
    p.add_argument("--all", action="store_true", help="All incomplete worker subtasks (default: first only)")
    args = p.parse_args()

    if str(ASANA) not in sys.path:
        sys.path.insert(0, str(ASANA))
    from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: WPS433

    load_env_from_dotfile()
    _ = get_token()

    pm_slug = DEPT_PM[args.department]
    subs = _run_fetch_list(args.parent)
    pending_workers: list[tuple[str, str, str]] = []
    for gid, name, done in subs:
        if done:
            continue
        assignee = _run_fetch_assignee(gid)
        if not assignee or assignee == pm_slug:
            continue
        pending_workers.append((gid, name, assignee))

    if not pending_workers:
        print(f"No incomplete worker subtasks under {args.parent} (PM={pm_slug}).")
        return 0

    targets = pending_workers if args.all else pending_workers[:1]
    for gid, name, worker in targets:
        print(f"--- {name} ({gid}) → {worker} ---")
        print(
            emit_snippet(
                department=args.department,
                parent_gid=args.parent,
                sub_gid=gid,
                worker_slug=worker,
            )
        )
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
