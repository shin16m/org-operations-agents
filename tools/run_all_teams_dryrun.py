#!/usr/bin/env python3
"""Run all-teams dryrun: bootstrap → planning sync → UX / analysis / development PM subtasks.

Each enabled worker posts comment_task + complete_task on their subtask.
Record: docs/verification/all-teams-dryrun.md

Usage (repo root):
  python tools/run_all_teams_dryrun.py
  python tools/run_all_teams_dryrun.py --skip-bootstrap   # reuse existing parent GID
  python tools/run_all_teams_dryrun.py --parent <GID>
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
PY = ROOT / ".venv/Scripts/python.exe"
if not PY.is_file():
    PY = Path(sys.executable)

# slug → SKILL.md (enabled agents in dryrun)
AGENT_SKILLS: dict[str, str] = {
    "workflow-orchestrator": "skills/platform/workflow-orchestrator/SKILL.md",
    "asana-buddy": "skills/platform/asana-buddy/SKILL.md",
    "task-dispatcher": "skills/platform/task-dispatcher/SKILL.md",
    "planning-pm": "skills/planning/planning-pm/SKILL.md",
    "issue-story-planner": "skills/planning/issue-story-planner/SKILL.md",
    "plan-reviewer": "skills/planning/plan-reviewer/SKILL.md",
    "ux-pm": "skills/ux/ux-pm/SKILL.md",
    "ux-designer": "skills/ux/ux-designer/SKILL.md",
    "ux-reviewer": "skills/ux/ux-reviewer/SKILL.md",
    "analytics-pm": "skills/analysis/analytics-pm/SKILL.md",
    "data-architect": "skills/analysis/data-architect/SKILL.md",
    "data-engineer": "skills/analysis/data-engineer/SKILL.md",
    "data-steward": "skills/analysis/data-steward/SKILL.md",
    "data-analyst": "skills/analysis/data-analyst/SKILL.md",
    "data-scientist": "skills/analysis/data-scientist/SKILL.md",
    "ml-engineer": "skills/analysis/ml-engineer/SKILL.md",
    "analysis-reviewer": "skills/analysis/analysis-reviewer/SKILL.md",
    "product-manager": "skills/development/product-manager/SKILL.md",
    "requirements-writer": "skills/development/requirements-writer/SKILL.md",
    "tech-designer": "skills/development/tech-designer/SKILL.md",
    "developer": "skills/development/developer/SKILL.md",
    "dev-reviewer": "skills/development/dev-reviewer/SKILL.md",
    "qa-verifier": "skills/development/qa-verifier/SKILL.md",
}

DEPT_PM: dict[str, str] = {
    "planning": "planning-pm",
    "ux": "ux-pm",
    "analysis": "analytics-pm",
    "development": "product-manager",
}

DEPT_PLANS: dict[str, Path] = {
    "ux": ROOT / "skills/ux/examples/assign-plan.web-app-v1.json",
    "analysis": ROOT / "skills/analysis/examples/assign-plan.dryrun-v1.json",
    "development": ROOT / "skills/development/examples/assign-plan.full-ui-v1.json",
}

DEPT_MARKERS: dict[str, tuple[str, ...]] = {
    "planning": ("企画", "planning"),
    "ux": ("UX", "ux"),
    "analysis": ("分析", "analysis"),
    "development": ("開発", "development", "full-ui"),
}


def _run(cmd: list[str], *, capture: bool = True) -> subprocess.CompletedProcess[str]:
    env = {**dict(**__import__("os").environ), "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=capture,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )


def _py(*args: str) -> list[str]:
    return [str(PY), str(ASANA / args[0]), *args[1:]]


def log(msg: str) -> None:
    print(msg, flush=True)


def comment_and_complete(gid: str, agent: str, summary: str, body: str) -> None:
    skill = AGENT_SKILLS.get(agent)
    if not skill:
        raise KeyError(f"No SKILL path for agent {agent!r}")
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
        log(r1.stderr or r1.stdout)
        raise RuntimeError(f"comment_task failed for {agent} on {gid}")
    log(f"  comment OK  {agent}  →  {gid}")
    r2 = _run(_py("complete_task.py", "--gid", gid, "-y"))
    if r2.returncode != 0:
        raise RuntimeError(f"complete_task failed for {gid}")
    log(f"  complete OK  {gid}")


def fetch_assignee(gid: str) -> str | None:
    r = _run(_py("fetch_task.py", "--gid", gid, "--show-assignee"))
    if r.returncode != 0:
        return None
    m = re.search(r"担当:\s*(\S+)", r.stdout)
    return m.group(1) if m else None


def list_subtask_gids(parent_gid: str) -> list[tuple[str, str, bool]]:
    r = _run(_py("fetch_task.py", "--gid", parent_gid, "--list-subtasks"))
    if r.returncode != 0:
        raise RuntimeError(f"list-subtasks failed for {parent_gid}")
    out: list[tuple[str, str, bool]] = []
    for line in r.stdout.splitlines():
        m = re.match(r"\[([ x])\]\s+(\d+)\s+(.+)$", line.strip())
        if m:
            out.append((m.group(2), m.group(3).strip(), m.group(1) == "x"))
    return out


def find_child_by_dept(epic_gid: str, dept: str) -> str | None:
    markers = DEPT_MARKERS[dept]
    for gid, name, _ in list_subtask_gids(epic_gid):
        low = name.lower()
        if any(m.lower() in low for m in markers):
            return gid
    return None


def pm_assign(parent_gid: str, plan: Path, department: str, pm_slug: str) -> None:
    r = _run(
        [
            str(PY),
            str(ASANA / "pm_assign_subtasks.py"),
            "--parent",
            parent_gid,
            "--plan",
            str(plan),
            "--department",
            department,
            "--update-parent-assignee",
            pm_slug,
            "-y",
        ]
    )
    if r.returncode != 0:
        log(r.stdout)
        log(r.stderr)
        raise RuntimeError(f"pm_assign_subtasks failed for {parent_gid}")
    log(r.stdout)


def run_worker_subtasks(parent_gid: str, pm_slug: str) -> list[str]:
    """Complete all incomplete subtasks with assignee != pm. Returns agents who worked."""
    worked: list[str] = []
    for gid, name, done in list_subtask_gids(parent_gid):
        if done:
            continue
        assignee = fetch_assignee(gid)
        if not assignee or assignee == pm_slug:
            continue
        _run(_py("fetch_task.py", "--gid", gid, "--show-assignee"))
        comment_and_complete(
            gid,
            assignee,
            f"dryrun complete — {assignee}",
            f"全チーム dryrun。サブタスク `{name}` を {assignee} が完了。",
        )
        worked.append(assignee)
    return worked


def add_dev_ux_dependency(dev_gid: str, ux_gid: str) -> None:
    if str(ASANA) not in sys.path:
        sys.path.insert(0, str(ASANA))
    from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: WPS433
    from asana_program_common import fetch_task, update_task_notes  # noqa: WPS433

    load_env_from_dotfile()
    token = get_token()
    task = fetch_task(dev_gid, token)
    body = (task.get("notes") or "").strip()
    for prefix in ("チーム:", "課:", "profile:", "担当:", "状態:"):
        pass  # keep body sections below header
    # strip existing header lines for clean merge
    lines = body.splitlines()
    while lines and (
        lines[0].startswith("チーム:")
        or lines[0].startswith("課:")
        or lines[0].startswith("profile:")
        or lines[0].startswith("担当:")
        or lines[0].startswith("状態:")
        or not lines[0].strip()
    ):
        lines.pop(0)
    body = "\n".join(lines).strip()
    stub_ux = ROOT / "output/dryrun/ux"
    stub_ux.mkdir(parents=True, exist_ok=True)
    (stub_ux / f"{ux_gid}-ux-spec.md").write_text("# UX spec dryrun stub\n", encoding="utf-8")
    (stub_ux / f"{ux_gid}-design-system.md").write_text("# Design System dryrun stub\n", encoding="utf-8")
    notes = (
        f"チーム: development\n\nprofile: full-ui\n担当: product-manager\n状態: in_progress\n\n"
        f"{body}\n\n"
        f"## 依存（読み取り専用）\n\n"
        f"| 種別 | 参照 | バージョン | 提供チーム |\n"
        f"|------|------|------------|------------|\n"
        f"| UX 仕様 | output/dryrun/ux/{ux_gid}-ux-spec.md | dryrun | ux |\n"
        f"| Design System | output/dryrun/ux/{ux_gid}-design-system.md | dryrun | ux |\n"
    )
    update_task_notes(dev_gid, notes.strip(), token)
    log(f"  dev notes updated with UX ## 依存 ({dev_gid})")


def bootstrap_epic() -> tuple[str, str]:
    r = _run(
        [
            str(PY),
            str(ASANA / "handoff_to_asana.py"),
            "--handoff",
            "docs/verification/fixtures/planning/handoff/bootstrap.all-teams-dryrun.json",
            "-y",
        ]
    )
    log(r.stdout)
    m = re.search(r"created_parent\s+(\d+)(?:\s+(https://\S+))?", r.stdout)
    if not m:
        raise RuntimeError("bootstrap did not return created_parent GID")
    return m.group(1), (m.group(2) or "")


def sync_handoff(parent_gid: str) -> None:
    r = _run(
        [
            str(PY),
            str(ASANA / "handoff_to_asana.py"),
            "--handoff",
            "docs/verification/fixtures/planning/handoff/handoff.all-teams-dryrun.json",
            "--require-review-result",
            "docs/verification/fixtures/planning/plan-review/plan-review.all-teams-dryrun.json",
            "--parent",
            parent_gid,
            "-y",
        ]
    )
    log(r.stdout)
    if r.returncode != 0:
        raise RuntimeError("handoff sync failed")


def run_dept_epic_child(epic_gid: str, dept: str, ux_gid: str | None = None) -> dict:
    child_gid = find_child_by_dept(epic_gid, dept)
    if not child_gid:
        raise RuntimeError(f"No Asana child for department {dept!r}")
    pm = DEPT_PM[dept]
    log(f"\n=== {dept} child {child_gid} ===")

    _run(_py("fetch_task.py", "--gid", child_gid, "--show-assignee"))
    comment_and_complete(
        child_gid,
        "task-dispatcher",
        f"dispatch → {pm}",
        f"DispatchRequest department={dept} · entry {pm}",
    )
    # undo complete so PM can run workflow on child
    _run(_py("complete_task.py", "--gid", child_gid, "--undo", "-y"))

    if dept == "development" and ux_gid:
        add_dev_ux_dependency(child_gid, ux_gid)

    if dept in DEPT_PLANS:
        pm_assign(child_gid, DEPT_PLANS[dept], dept, pm)
        worked = run_worker_subtasks(child_gid, pm)
        comment_and_complete(
            child_gid,
            pm,
            f"{pm} — DeptWorkComplete",
            f"全サブ完了。department={dept} dryrun。",
        )
        return {"child_gid": child_gid, "workers": worked}

    # planning: no nested PM plan — planner/reviewer/pm comments
    comment_and_complete(
        child_gid,
        "issue-story-planner",
        "Handoff 作成",
        "handoff.all-teams-dryrun.json を出力。",
    )
    _run(_py("complete_task.py", "--gid", child_gid, "--undo", "-y"))
    comment_and_complete(
        child_gid,
        "plan-reviewer",
        "PlanReview passed_with_notes",
        "plan-review.all-teams-dryrun.json",
    )
    _run(_py("complete_task.py", "--gid", child_gid, "--undo", "-y"))
    comment_and_complete(
        child_gid,
        pm,
        "planning-pm — sync 完了",
        "handoff sync 済み。execution 系子作成。",
    )
    return {"child_gid": child_gid, "workers": ["issue-story-planner", "plan-reviewer", pm]}


def write_report(
    epic_gid: str,
    results: dict,
    *,
    epic_url: str = "",
    command: str = "python tools/run_all_teams_dryrun.py",
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# 全チーム dryrun — 実行記録",
        "",
        f"実施: {now}",
        "",
        "## 目的",
        "",
        "4 L3 チーム（planning / ux / analysis / development）+ プラットフォーム配賦で、"
        "各 enabled slug が `comment_task` → `complete_task` まで到達することを Asana 上で確認する。",
        "",
        "## 実行",
        "",
        "```powershell",
        "$env:PYTHONIOENCODING='utf-8'",
        command,
        "```",
        "",
        "## fixture",
        "",
        "| 種別 | パス |",
        "|------|------|",
        "| bootstrap Handoff | `docs/verification/fixtures/planning/handoff/bootstrap.all-teams-dryrun.json` |",
        "| 本番 Handoff | `docs/verification/fixtures/planning/handoff/handoff.all-teams-dryrun.json` |",
        "| PlanReview | `docs/verification/fixtures/planning/plan-review/plan-review.all-teams-dryrun.json` |",
        "",
        "## Asana",
        "",
        "| 項目 | 値 |",
        "|------|-----|",
        f"| 親エピック GID | `{epic_gid}` |",
    ]
    if epic_url:
        lines.append(f"| 親 URL | {epic_url} |")
    lines.extend(["", "## 段階別結果", ""])
    for dept, info in results.items():
        lines.append(f"### {dept}")
        lines.append("")
        lines.append(f"- child GID: `{info['child_gid']}`")
        workers = info.get("workers", [])
        if workers:
            lines.append(f"- workers: {', '.join(workers)}")
        lines.append("")
    all_workers = sorted(set(a for i in results.values() for a in i.get("workers", [])))
    lines.extend(
        [
            "## 参加 slug 一覧",
            "",
            ", ".join(all_workers) if all_workers else "（なし）",
            "",
            "## 関連",
            "",
            "- [`run_all_teams_dryrun.py`](../../tools/run_all_teams_dryrun.py)",
            "- [`handoff.all-teams-dryrun.json`](../../docs/verification/fixtures/planning/handoff/handoff.all-teams-dryrun.json)",
            "- 索引: [`docs/verification/README.md`](README.md)",
            "",
        ]
    )
    out = ROOT / "docs/verification/all-teams-dryrun.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    log(f"\nReport: {out}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--parent", help="Existing epic GID (skip bootstrap)")
    p.add_argument("--skip-bootstrap", action="store_true")
    p.add_argument(
        "--from-dept",
        choices=("planning", "ux", "analysis", "development"),
        help="Skip earlier departments (requires --parent)",
    )
    args = p.parse_args()

    if args.parent:
        epic_gid = args.parent
        epic_url = ""
    elif args.skip_bootstrap:
        p.error("--skip-bootstrap requires --parent")
    else:
        log("=== bootstrap ===")
        epic_gid, epic_url = bootstrap_epic()

    log(f"Epic GID: {epic_gid}")
    if epic_url:
        log(f"Epic URL: {epic_url}")

    dept_order = ("planning", "ux", "analysis", "development")
    start_idx = dept_order.index(args.from_dept) if args.from_dept else 0

    if start_idx == 0 and not args.from_dept:
        comment_and_complete(
            epic_gid,
            "workflow-orchestrator",
            "intake — 全チーム dryrun 開始",
            "bootstrap / planning / ux / analysis / development を順次実行。",
        )
        _run(_py("complete_task.py", "--gid", epic_gid, "--undo", "-y"))

        log("\n=== handoff sync (asana-buddy / planning-pm) ===")
        sync_handoff(epic_gid)
        comment_and_complete(
            epic_gid,
            "asana-buddy",
            "handoff sync 完了",
            "handoff.all-teams-dryrun.json を親に sync。",
        )
        _run(_py("complete_task.py", "--gid", epic_gid, "--undo", "-y"))

    results: dict = {}
    ux_gid: str | None = None
    if start_idx <= 0:
        results["planning"] = run_dept_epic_child(epic_gid, "planning")
    if start_idx <= 1:
        results["ux"] = run_dept_epic_child(epic_gid, "ux")
        ux_gid = results["ux"]["child_gid"]
    elif start_idx <= 3:
        ux_gid = find_child_by_dept(epic_gid, "ux")
    if start_idx <= 2:
        results["analysis"] = run_dept_epic_child(epic_gid, "analysis")
    if start_idx <= 3:
        if not ux_gid:
            ux_gid = find_child_by_dept(epic_gid, "ux") or ""
        results["development"] = run_dept_epic_child(
            epic_gid, "development", ux_gid=ux_gid or None
        )

    comment_and_complete(
        epic_gid,
        "workflow-orchestrator",
        "全チーム dryrun 完了",
        "planning / ux / analysis / development 全サブ完了。",
    )

    write_report(epic_gid, results, epic_url=epic_url, command=" ".join(sys.argv))
    log("\nDONE.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
