#!/usr/bin/env python3
"""Milestone tracker complete hook — readiness evaluation WARN/BLOCK (MS3).

Runs before complete_task on governance milestone tracker subtasks.

Usage:
  python tools/epic_milestone_readiness_hook.py --task <TRACKER_SUBTASK_GID>
  python tools/epic_milestone_readiness_hook.py --task <GID> --dry-run
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
OPTIONAL = ROOT / "skills/platform/asana-buddy/optional"
PY = ROOT / ".venv/Scripts/python.exe"
if not PY.is_file():
    PY = Path(sys.executable)

for p in (str(TOOLS), str(OPTIONAL)):
    if p not in sys.path:
        sys.path.insert(0, p)

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import console_safe, create_task_story  # noqa: E402

WARN_MARKER = "org-ops WARN milestone-readiness"

CHECKLIST_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"\[M4\]|m4-enforcement", re.I),
        "docs/verification/fixtures/milestone-readiness/m4-enforcement.json",
    ),
    (
        re.compile(r"\[M5\]|m5-learning-loop", re.I),
        "docs/verification/fixtures/milestone-readiness/m5-learning-loop.json",
    ),
    (
        re.compile(r"\[M6\]|m6-kpi", re.I),
        "docs/verification/fixtures/milestone-readiness/m6-kpi-measurement.json",
    ),
    (
        re.compile(r"\[MS1\]", re.I),
        "docs/verification/fixtures/milestone-readiness/m4-enforcement.json",
    ),
    (
        re.compile(r"\[MS2\]", re.I),
        "docs/verification/fixtures/milestone-readiness/m5-learning-loop.json",
    ),
    (
        re.compile(r"\[M6\]|m6-kpi", re.I),
        "docs/verification/fixtures/milestone-readiness/m6-kpi-measurement.json",
    ),
    (
        re.compile(r"\[M7\]|m7-ops", re.I),
        "docs/verification/fixtures/milestone-readiness/m7-ops-hardening.json",
    ),
    (
        re.compile(r"\[M8\]|m8-quality", re.I),
        "docs/verification/fixtures/milestone-readiness/m8-quality-ssot.json",
    ),
    (
        re.compile(r"\[M9\]|m9-completion", re.I),
        "docs/verification/fixtures/milestone-readiness/m9-completion-100.json",
    ),
    (
        re.compile(r"\[MS4\]", re.I),
        "docs/verification/fixtures/milestone-readiness/m6-kpi-measurement.json",
    ),
    (
        re.compile(r"\[MS5\]", re.I),
        "docs/verification/fixtures/milestone-readiness/m9-completion-100.json",
    ),
]


@dataclass(frozen=True)
class ReadinessEvaluation:
    kind: str  # ok | warn | not_achieved | skip
    message: str
    score: float | None = None
    checklist: str | None = None
    check_exit: int = 0


def _block_on_failure() -> bool:
    return os.environ.get("ORG_OPS_MILESTONE_READINESS_BLOCK", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _fetch_task_text(task_gid: str) -> tuple[str, str]:
    r = subprocess.run(
        [str(PY), str(OPTIONAL / "fetch_task.py"), "--gid", task_gid],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout or "fetch_task failed")
    title = ""
    notes = ""
    for line in r.stdout.splitlines():
        if line.startswith("name:"):
            title = line.split(":", 1)[1].strip()
    if "--- notes ---" in r.stdout:
        notes = r.stdout.split("--- notes ---", 1)[1]
    return title, notes


def is_milestone_tracker(title: str, notes: str) -> bool:
    if re.search(r"milestone_tracker:\s*true", notes, re.I):
        return True
    if re.search(r"—\s*マイルストーン", title):
        return True
    if re.search(r"\[(M\d+|MS\d+)\]", title):
        return True
    return False


def resolve_checklist(title: str, notes: str) -> str | None:
    m = re.search(r"checklist:\s*(\S+\.json)", notes, re.I)
    if m:
        return m.group(1)
    blob = f"{title}\n{notes}"
    for pattern, path in CHECKLIST_PATTERNS:
        if pattern.search(blob):
            return path
    return None


def run_readiness_check(
    task_gid: str,
    checklist_rel: str,
    *,
    strict: bool,
) -> tuple[int, str]:
    out_rel = f"output/governance/milestone-reports/{task_gid}-readiness.json"
    cmd = [
        str(PY),
        str(TOOLS / "check_milestone_readiness.py"),
        "--checklist",
        checklist_rel,
        "--tracker-gid",
        task_gid,
        "--out",
        out_rel,
    ]
    if strict:
        cmd.append("--strict")
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    summary = (r.stderr or "").strip().splitlines()
    last = summary[-1] if summary else f"exit {r.returncode}"
    return int(r.returncode), last


def evaluate_task(task_gid: str) -> ReadinessEvaluation:
    title, notes = _fetch_task_text(task_gid)
    if not is_milestone_tracker(title, notes):
        return ReadinessEvaluation(
            kind="skip",
            message=f"not a milestone tracker: {console_safe(title[:60])}",
        )

    checklist = resolve_checklist(title, notes)
    if not checklist:
        return ReadinessEvaluation(
            kind="warn",
            message=(
                "milestone tracker だが checklist 未解決。"
                " notes に checklist: <path> を追加するかタイトルに [M4]/[M5]/[MSn] を含めてください。"
            ),
        )

    exit_code, summary = run_readiness_check(
        task_gid,
        checklist,
        strict=_block_on_failure(),
    )
    score = None
    m = re.search(r"score=([0-9.]+)", summary)
    if m:
        score = float(m.group(1))

    if exit_code == 0:
        return ReadinessEvaluation(
            kind="ok",
            message=f"milestone readiness OK — {summary}",
            score=score,
            checklist=checklist,
            check_exit=0,
        )

    kind = "not_achieved" if score is not None and score < 70 else "warn"
    return ReadinessEvaluation(
        kind=kind,
        message=(
            f"milestone readiness 未達 — {summary}。"
            f" レポート: output/governance/milestone-reports/{task_gid}-readiness.json"
        ),
        score=score,
        checklist=checklist,
        check_exit=exit_code,
    )


def build_warn_comment(evaluation: ReadinessEvaluation) -> str | None:
    if evaluation.kind in ("ok", "skip"):
        return None
    return f"{WARN_MARKER}\n\n{evaluation.message}"


def run_milestone_readiness_hook(
    task_gid: str,
    *,
    token: str | None = None,
    dry_run: bool = False,
) -> int:
    if token is None:
        load_env_from_dotfile()
        token = get_token()

    evaluation = evaluate_task(task_gid)
    if evaluation.kind == "skip":
        print(console_safe(f"SKIP  milestone_readiness  {evaluation.message}"))
        return 0

    warn_text = build_warn_comment(evaluation)
    if warn_text:
        if dry_run:
            print(f"DRY-RUN  warn_comment  task={task_gid}\n{warn_text}")
        else:
            create_task_story(task_gid, warn_text, token)
            print(console_safe(f"WARN  milestone_readiness  task={task_gid}  comment posted"))
        print(
            console_safe(
                f"WARN  milestone_readiness  kind={evaluation.kind}  "
                f"score={evaluation.score}  checklist={evaluation.checklist}"
            )
        )

    if evaluation.kind == "ok":
        return 0

    if _block_on_failure():
        print(
            console_safe(
                "ERROR  milestone_readiness  blocked  "
                "(ORG_OPS_MILESTONE_READINESS_BLOCK=1)"
            ),
            file=sys.stderr,
        )
        return 1
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Milestone tracker readiness WARN/BLOCK hook")
    p.add_argument("--task", required=True, help="Tracker subtask GID")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    return run_milestone_readiness_hook(args.task, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
