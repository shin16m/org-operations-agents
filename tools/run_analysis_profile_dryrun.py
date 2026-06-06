#!/usr/bin/env python3
"""Analysis delivery v2 profile dryrun: insights / catalog / model-serve.

Record: docs/verification/analysis-profile-dryrun.md

Usage (repo root):
  python tools/run_analysis_profile_dryrun.py --profile catalog
  python tools/run_analysis_profile_dryrun.py --profile insights
  python tools/run_analysis_profile_dryrun.py --profile model-serve
  python tools/run_analysis_profile_dryrun.py --profile all
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
ASANA = ROOT / "skills/platform/asana-buddy/optional"
if str(ASANA) not in sys.path:
    sys.path.insert(0, str(ASANA))
PY = ROOT / ".venv/Scripts/python.exe"
if not PY.is_file():
    PY = Path(sys.executable)

BOOTSTRAP = ROOT / "docs/verification/fixtures/planning/handoff/bootstrap.analysis-v2-dryrun.json"
PM_SLUG = "analytics-pm"

PROFILE_PLANS: dict[str, tuple[str, int]] = {
    "catalog": ("skills/analysis/examples/assign-plan.catalog-v2.json", 7),
    "insights": ("skills/analysis/examples/assign-plan.insights-v2.json", 11),
    "model-serve": ("skills/analysis/examples/assign-plan.model-serve-v2.json", 14),
}

AGENT_SKILLS: dict[str, str] = {
    "task-dispatcher": "skills/platform/task-dispatcher/SKILL.md",
    "analytics-pm": "skills/analysis/analytics-pm/SKILL.md",
    "analytics-requirements-writer": "skills/analysis/analytics-requirements-writer/SKILL.md",
    "data-architect": "skills/analysis/data-architect/SKILL.md",
    "data-engineer": "skills/analysis/data-engineer/SKILL.md",
    "data-steward": "skills/analysis/data-steward/SKILL.md",
    "data-analyst": "skills/analysis/data-analyst/SKILL.md",
    "data-scientist": "skills/analysis/data-scientist/SKILL.md",
    "ml-engineer": "skills/analysis/ml-engineer/SKILL.md",
    "analysis-reviewer": "skills/analysis/analysis-reviewer/SKILL.md",
}


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    env = {**dict(**__import__("os").environ), "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )


def _py(*args: str) -> list[str]:
    return [str(PY), str(ASANA / args[0]), *args[1:]]


def log(msg: str) -> None:
    print(msg, flush=True)


def agent_comment_body(*, actions: list[str], artifacts: list[str] | None = None) -> str:
    from asana_program_common import build_human_comment_body

    return build_human_comment_body(actions=actions, artifacts=artifacts)


def comment_and_complete(gid: str, agent: str, summary: str, body: str) -> None:
    skill = AGENT_SKILLS[agent]
    r1 = _run(
        _py(
            "comment_task.py",
            "--gid",
            gid,
            "--agent",
            agent,
            "--skill",
            skill,
            "--summary",
            summary,
            "--body",
            body,
            "-y",
        )
    )
    if r1.returncode != 0:
        raise RuntimeError(f"comment_task failed: {agent} {gid}\n{r1.stderr or r1.stdout}")
    r2 = _run(_py("complete_task.py", "--gid", gid, "--skip-worker-guards", "-y"))
    if r2.returncode != 0:
        raise RuntimeError(f"complete_task failed: {gid}\n{r2.stderr or r2.stdout}")


def list_subtasks(parent_gid: str) -> list[tuple[str, str, bool]]:
    r = _run(_py("fetch_task.py", "--gid", parent_gid, "--list-subtasks"))
    if r.returncode != 0:
        raise RuntimeError(f"list-subtasks failed: {parent_gid}")
    out: list[tuple[str, str, bool]] = []
    for line in r.stdout.splitlines():
        m = re.match(r"\[([ x])\]\s+(\d+)\s+(.+)$", line.strip())
        if m:
            out.append((m.group(2), m.group(3).strip(), m.group(1) == "x"))
    return out


def fetch_assignee(gid: str) -> str | None:
    r = _run(_py("fetch_task.py", "--gid", gid, "--show-assignee"))
    if r.returncode != 0:
        return None
    m = re.search(r"担当:\s*(\S+)", r.stdout)
    return m.group(1) if m else None


def find_analysis_child(epic_gid: str) -> str | None:
    for gid, name, _ in list_subtasks(epic_gid):
        if "分析" in name or "analysis" in name.lower():
            return gid
    return None


def bootstrap_epic() -> tuple[str, str]:
    r = _run(_py("handoff_to_asana.py", "--handoff", str(BOOTSTRAP.relative_to(ROOT)), "-y"))
    log(r.stdout)
    m = re.search(r"created_parent\s+(\d+)", r.stdout)
    if not m:
        raise RuntimeError("bootstrap did not return created_parent GID")
    epic_gid = m.group(1)
    child = find_analysis_child(epic_gid)
    if not child:
        raise RuntimeError("analysis child not found")
    return epic_gid, child


def pm_assign(parent_gid: str, plan_rel: str) -> None:
    plan = ROOT / plan_rel
    r = _run(
        [
            str(PY),
            str(ASANA / "pm_assign_subtasks.py"),
            "--parent",
            parent_gid,
            "--plan",
            str(plan),
            "--department",
            "analysis",
            "--update-parent-assignee",
            PM_SLUG,
            "-y",
        ]
    )
    log(r.stdout)
    if r.returncode != 0:
        raise RuntimeError(f"pm_assign_subtasks failed\n{r.stderr or r.stdout}")


def run_workers(parent_gid: str) -> list[str]:
    worked: list[str] = []
    for gid, name, done in list_subtasks(parent_gid):
        if done:
            continue
        assignee = fetch_assignee(gid)
        if not assignee or assignee == PM_SLUG:
            continue
        comment_and_complete(
            gid,
            assignee,
            f"analysis profile dryrun — {assignee}",
            agent_comment_body(
                actions=[f"サブタスク `{name}` profile dryrun 完了"],
                artifacts=[f"Asana subtask GID {gid}"],
            ),
        )
        worked.append(assignee)
        log(f"  worker OK  {assignee}  →  {gid}")
    return worked


def verify_subtask_count(parent_gid: str, expected: int) -> list[str]:
    assignees: list[str] = []
    for gid, name, _ in list_subtasks(parent_gid):
        a = fetch_assignee(gid)
        if a and a != PM_SLUG:
            assignees.append(a)
            log(f"  sub {gid}  {name}  →  {a}")
    if len(assignees) != expected:
        raise RuntimeError(f"expected {expected} worker subtasks, got {len(assignees)}")
    if "analytics-requirements-writer" not in assignees:
        raise RuntimeError("analytics-requirements-writer missing (PM separation)")
    return assignees


def run_profile(profile: str, analysis_gid: str | None = None) -> dict:
    plan_rel, expected_count = PROFILE_PLANS[profile]
    if analysis_gid is None:
        log(f"\n=== bootstrap ({profile}) ===")
        epic_gid, analysis_gid = bootstrap_epic()
    else:
        epic_gid = ""

    log(f"\n=== {profile} — analysis child {analysis_gid} ===")
    comment_and_complete(
        analysis_gid,
        "task-dispatcher",
        f"dispatch → analytics-pm ({profile})",
        agent_comment_body(actions=[f"profile={profile} dryrun dispatch"]),
    )
    _run(_py("complete_task.py", "--gid", analysis_gid, "--undo", "-y"))

    pm_assign(analysis_gid, plan_rel)
    assignees = verify_subtask_count(analysis_gid, expected_count)
    workers = run_workers(analysis_gid)
    comment_and_complete(
        analysis_gid,
        PM_SLUG,
        f"analytics-pm — DeptWorkComplete ({profile})",
        agent_comment_body(
            actions=[f"profile={profile} 全サブ完了"],
            artifacts=[plan_rel],
        ),
    )
    return {
        "profile": profile,
        "epic_gid": epic_gid,
        "analysis_gid": analysis_gid,
        "plan": plan_rel,
        "expected_count": expected_count,
        "assignees": assignees,
        "workers": workers,
    }


def write_report(results: list[dict], command: str) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Analysis profile dryrun — 実行記録",
        "",
        f"実施: {now}",
        "",
        "## 目的",
        "",
        "`analysis-delivery` v2 の **insights / catalog / model-serve** profile について、"
        "assign plan どおりのサブタスク数・担当 slug が Asana 上で到達することを確認する。",
        "",
        "## 実行",
        "",
        "```powershell",
        "$env:PYTHONIOENCODING='utf-8'",
        command,
        "```",
        "",
        "## 手順（単体）",
        "",
        "```powershell",
        "python tools/run_analysis_profile_dryrun.py --profile catalog",
        "python tools/run_analysis_profile_dryrun.py --profile insights",
        "python tools/run_analysis_profile_dryrun.py --profile model-serve",
        "```",
        "",
        "## 結果",
        "",
    ]
    for r in results:
        lines.extend(
            [
                f"### profile: `{r['profile']}`",
                "",
                f"- assign plan: `{r['plan']}`",
                f"- 分析子 GID: `{r['analysis_gid']}`",
                f"- サブタスク数: {r['expected_count']}",
                f"- workers: {', '.join(r['workers'])}",
                "",
            ]
        )
    lines.extend(
        [
            "## 関連",
            "",
            "- [`analysis-delivery-v2-dryrun.md`](analysis-delivery-v2-dryrun.md)（full profile）",
            "- [`analytics-pm-assignment.md`](../design/analytics-pm-assignment.md)",
            "- [`run_analysis_profile_dryrun.py`](../../tools/run_analysis_profile_dryrun.py)",
            "",
        ]
    )
    out = ROOT / "docs/verification/analysis-profile-dryrun.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    log(f"\nReport: {out}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--profile",
        choices=("catalog", "insights", "model-serve", "all"),
        default="catalog",
        help="Analysis delivery profile to dryrun",
    )
    p.add_argument("--analysis-child", help="Reuse existing analysis child GID")
    args = p.parse_args()

    profiles = list(PROFILE_PLANS) if args.profile == "all" else [args.profile]
    results: list[dict] = []
    for prof in profiles:
        results.append(run_profile(prof, args.analysis_child if len(profiles) == 1 else None))

    write_report(results, " ".join(sys.argv))
    log("\nDONE.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as e:
        log(f"ERROR: {e}")
        raise SystemExit(1)
