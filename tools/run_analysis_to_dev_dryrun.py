#!/usr/bin/env python3
"""Analysis → development seam dryrun: model-serve complete → ## 依存 transfer → dev full.

Record: docs/verification/cross-team/analysis-to-dev-dryrun.md

Usage (repo root):
  python tools/run_analysis_to_dev_dryrun.py
  python tools/run_analysis_to_dev_dryrun.py --parent <EPIC_GID>
  python tools/run_analysis_to_dev_dryrun.py --parent <EPIC_GID> --from-dev
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

BOOTSTRAP = ROOT / "docs/verification/fixtures/planning/handoff/bootstrap.analysis-to-dev-dryrun.json"
ANALYSIS_PLAN = ROOT / "skills/analysis/examples/assign-plan.model-serve-v2.json"
DEV_PLAN = ROOT / "skills/development/examples/assign-plan.analysis-consume-dryrun.json"
ANALYSIS_PM = "analytics-pm"
DEV_PM = "product-manager"
EXPECTED_ANALYSIS_WORKERS = 14

API_STUB = "https://api.example.com/dryrun/analysis-to-dev/v1/predict"
SLA_STUB = "日次更新・遅延最大 2h"

AGENT_SKILLS: dict[str, str] = {
    "task-dispatcher": "skills/platform/task-dispatcher/SKILL.md",
    "analytics-pm": "skills/analysis/analytics-pm/SKILL.md",
    "analytics-requirements-writer": "skills/analysis/analytics-requirements-writer/SKILL.md",
    "data-architect": "skills/analysis/data-architect/SKILL.md",
    "data-engineer": "skills/analysis/data-engineer/SKILL.md",
    "data-steward": "skills/analysis/data-steward/SKILL.md",
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


def fetch_notes(gid: str) -> str:
    from agent_handler_asana import get_token, load_env_from_dotfile
    from asana_program_common import fetch_task

    load_env_from_dotfile()
    task = fetch_task(gid, get_token())
    return (task.get("notes") or "").strip()


def find_child(epic_gid: str, *, analysis: bool) -> str | None:
    for gid, name, _ in list_subtasks(epic_gid):
        low = name.lower()
        if analysis and ("分析" in name or "analysis" in low):
            return gid
        if not analysis and ("開発" in name or "development" in low or "dev" in low):
            return gid
    return None


def bootstrap_epic() -> tuple[str, str, str]:
    r = _run(_py("handoff_to_asana.py", "--handoff", str(BOOTSTRAP.relative_to(ROOT)), "-y"))
    log(r.stdout)
    m = re.search(r"created_parent\s+(\d+)", r.stdout)
    if not m:
        raise RuntimeError("bootstrap did not return created_parent GID")
    epic_gid = m.group(1)
    analysis_gid = find_child(epic_gid, analysis=True)
    dev_gid = find_child(epic_gid, analysis=False)
    if not analysis_gid or not dev_gid:
        raise RuntimeError(f"children missing: analysis={analysis_gid} dev={dev_gid}")
    return epic_gid, analysis_gid, dev_gid


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
    log(r.stdout)
    if r.returncode != 0:
        raise RuntimeError(f"pm_assign_subtasks failed\n{r.stderr or r.stdout}")


def run_workers(parent_gid: str, pm_slug: str) -> list[str]:
    worked: list[str] = []
    for gid, name, done in list_subtasks(parent_gid):
        if done:
            continue
        assignee = fetch_assignee(gid)
        if not assignee or assignee == pm_slug:
            continue
        comment_and_complete(
            gid,
            assignee,
            f"analysis-to-dev dryrun — {assignee}",
            agent_comment_body(
                actions=[f"サブタスク `{name}` dryrun 完了"],
                artifacts=[f"Asana subtask GID {gid}"],
            ),
        )
        worked.append(assignee)
        log(f"  worker OK  {assignee}  →  {gid}")
    return worked


def write_analysis_stubs(analysis_gid: str) -> list[str]:
    stub_dir = ROOT / "output/dryrun/analysis"
    stub_dir.mkdir(parents=True, exist_ok=True)
    catalog = stub_dir / f"{analysis_gid}-catalog.md"
    model = stub_dir / f"{analysis_gid}-model-stub.md"
    release = stub_dir / f"{analysis_gid}-release.md"
    catalog.write_text(
        f"# Catalog dryrun\n\nSLA: {SLA_STUB}\n",
        encoding="utf-8",
    )
    model.write_text("# Model card dryrun stub\n", encoding="utf-8")
    release.write_text(f"# Release dryrun\n\nAPI: {API_STUB}\n", encoding="utf-8")
    return [
        catalog.relative_to(ROOT).as_posix(),
        model.relative_to(ROOT).as_posix(),
        API_STUB,
        SLA_STUB,
    ]


def verify_analysis_subtasks(analysis_gid: str) -> None:
    count = sum(
        1
        for gid, _, _ in list_subtasks(analysis_gid)
        if (a := fetch_assignee(gid)) and a != ANALYSIS_PM
    )
    if count != EXPECTED_ANALYSIS_WORKERS:
        raise RuntimeError(f"expected {EXPECTED_ANALYSIS_WORKERS} analysis subs, got {count}")


def transfer_analysis_dependency(dev_gid: str, analysis_gid: str) -> None:
    from agent_handler_asana import get_token, load_env_from_dotfile
    from asana_program_common import fetch_task, update_task_notes

    artifacts = write_analysis_stubs(analysis_gid)
    load_env_from_dotfile()
    token = get_token()
    task = fetch_task(dev_gid, token)
    body = (task.get("notes") or "").strip()
    lines = body.splitlines()
    while lines and (
        lines[0].startswith(("チーム:", "課:", "profile:", "担当:", "状態:")) or not lines[0].strip()
    ):
        lines.pop(0)
    body = "\n".join(lines).strip()
    notes = (
        f"チーム: development\n\nprofile: full\n担当: {DEV_PM}\n状態: in_progress\n\n"
        f"{body}\n\n"
        f"## 依存（読み取り専用）\n\n"
        f"| 種別 | 参照 | バージョン | 提供チーム |\n"
        f"|------|------|------------|------------|\n"
        f"| データカタログ | {artifacts[0]} | dryrun | analysis |\n"
        f"| モデル | {artifacts[1]} | dryrun | analysis |\n"
        f"| 推論 API | {API_STUB} | dryrun | analysis |\n"
        f"| SLA | {SLA_STUB} | — | analysis |\n"
    )
    update_task_notes(dev_gid, notes.strip(), token)
    log(f"  dev notes updated with analysis ## 依存 ({dev_gid})")


def verify_dev_dependency(dev_gid: str, analysis_gid: str) -> None:
    notes = fetch_notes(dev_gid)
    catalog_path = f"output/dryrun/analysis/{analysis_gid}-catalog.md"
    required = [
        "## 依存（読み取り専用）",
        catalog_path,
        API_STUB,
        SLA_STUB,
        "profile: full",
    ]
    missing = [r for r in required if r not in notes]
    if missing:
        raise RuntimeError(f"dev dependency verification failed — missing: {missing}")
    log("  verify OK — dev notes contain ## 依存 + API URL + catalog")


def run_analysis_phase(analysis_gid: str) -> list[str]:
    comment_and_complete(
        analysis_gid,
        "task-dispatcher",
        "dispatch → analytics-pm",
        agent_comment_body(actions=["analysis→dev dryrun dispatch"]),
    )
    _run(_py("complete_task.py", "--gid", analysis_gid, "--undo", "-y"))
    pm_assign(analysis_gid, ANALYSIS_PLAN, "analysis", ANALYSIS_PM)
    verify_analysis_subtasks(analysis_gid)
    workers = run_workers(analysis_gid, ANALYSIS_PM)
    artifacts = write_analysis_stubs(analysis_gid)
    comment_and_complete(
        analysis_gid,
        ANALYSIS_PM,
        "analytics-pm — DeptWorkComplete (model-serve)",
        agent_comment_body(
            actions=["model-serve 完了 · catalog / model / API を artifacts に公開"],
            artifacts=artifacts,
        ),
    )
    return workers


def has_worker_subtasks(parent_gid: str, pm_slug: str) -> bool:
    for gid, _, _ in list_subtasks(parent_gid):
        a = fetch_assignee(gid)
        if a and a != pm_slug:
            return True
    return False


def run_dev_phase(dev_gid: str, analysis_gid: str) -> list[str]:
    assignee = fetch_assignee(dev_gid)
    if assignee != DEV_PM:
        comment_and_complete(
            dev_gid,
            "task-dispatcher",
            "dispatch → product-manager",
            agent_comment_body(
                actions=[
                    "DispatchRequest（department=development）を解決",
                    "分析子完了を前提に product-manager へ委譲",
                ],
            ),
        )
        _run(_py("complete_task.py", "--gid", dev_gid, "--undo", "-y"))

    transfer_analysis_dependency(dev_gid, analysis_gid)
    verify_dev_dependency(dev_gid, analysis_gid)

    if not has_worker_subtasks(dev_gid, DEV_PM):
        pm_assign(dev_gid, DEV_PLAN, "development", DEV_PM)
    else:
        log("  pm_assign skipped — worker subtasks already exist")
    workers = run_workers(dev_gid, DEV_PM)
    comment_and_complete(
        dev_gid,
        DEV_PM,
        "product-manager — DeptWorkComplete (analysis consume dryrun)",
        agent_comment_body(
            actions=["full profile 完了 · 分析 ## 依存 を read-only で consume"],
            artifacts=[f"analysis child {analysis_gid}", API_STUB],
        ),
    )
    return workers


def write_report(
    *,
    epic_gid: str,
    analysis_gid: str,
    dev_gid: str,
    analysis_workers: list[str],
    dev_workers: list[str],
    command: str,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# 分析 → development — 継ぎ目 dryrun",
        "",
        f"実施: {now}",
        "",
        "## 目的",
        "",
        "分析子（`profile: model-serve`）完了後、**product-manager が `## 依存` に"
        " catalog / model / API URL を転記 → development `profile: full` 着手**"
        "までのチーム間継ぎ目を Asana 上で確認する。",
        "",
        "> **API URL:** dryrun stub（`api.example.com`）は実在しません。",
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
        f"| bootstrap | `{BOOTSTRAP.relative_to(ROOT).as_posix()}` |",
        f"| Handoff 例 | `skills/planning/issue-story-planner/examples/handoff.analysis-model-serve.json` |",
        f"| 分析 assign plan | `{ANALYSIS_PLAN.relative_to(ROOT).as_posix()}` |",
        f"| 開発 assign plan | `{DEV_PLAN.relative_to(ROOT).as_posix()}` |",
        "",
        "## Asana",
        "",
        "| 項目 | GID |",
        "|------|-----|",
        f"| 親エピック | `{epic_gid}` |",
        f"| 分析子（model-serve） | `{analysis_gid}` |",
        f"| 開発子（full） | `{dev_gid}` |",
        "",
        "## 継ぎ目チェック",
        "",
        "- [x] 分析子: model-serve 14 サブ完了 · API URL を artifacts に含む",
        "- [x] 開発子: `## 依存（読み取り専用）` に catalog / model / API URL / SLA",
        "- [x] 開発子: `profile: full` ヘッダのあとに依存表",
        f"- [x] API stub: `{API_STUB}`",
        "- [x] product-manager が pm_assign 後、開発ワーカーが comment → complete",
        "",
        "## 結果",
        "",
        f"- analysis workers（{len(analysis_workers)}）: {', '.join(analysis_workers)}",
        f"- dev workers: {', '.join(dev_workers)}",
        "",
        "## 関連",
        "",
        "- [`cross-team-artifact-bridge.md`](../design/cross-team-artifact-bridge.md)",
        "- [`handoff.analysis-model-serve.json`](../../skills/planning/issue-story-planner/examples/handoff.analysis-model-serve.json)",
        "- [`analysis-profile-dryrun.md`](../analysis/analysis-profile-dryrun.md)",
        "- [`ux-to-dev-full-ui-dryrun.md`](../cross-team/ux-to-dev-full-ui-dryrun.md)",
        "- [`run_analysis_to_dev_dryrun.py`](../../tools/run_analysis_to_dev_dryrun.py)",
        "",
    ]
    out = ROOT / "docs/verification/cross-team/analysis-to-dev-dryrun.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    log(f"\nReport: {out}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--parent", help="Existing epic GID")
    p.add_argument(
        "--from-dev",
        action="store_true",
        help="Skip analysis phase (requires --parent)",
    )
    args = p.parse_args()

    if args.from_dev and not args.parent:
        p.error("--from-dev requires --parent")

    if args.parent:
        epic_gid = args.parent
        analysis_gid = find_child(epic_gid, analysis=True)
        dev_gid = find_child(epic_gid, analysis=False)
        if not analysis_gid or not dev_gid:
            raise SystemExit(f"analysis/dev children not found under {epic_gid}")
    else:
        log("=== bootstrap ===")
        epic_gid, analysis_gid, dev_gid = bootstrap_epic()

    log(f"Epic: {epic_gid}  analysis: {analysis_gid}  dev: {dev_gid}")

    if args.from_dev:
        log("\n=== analysis phase — skipped (--from-dev) ===")
        analysis_workers = ["(skipped)"]
    else:
        log("\n=== analysis phase (model-serve) ===")
        analysis_workers = run_analysis_phase(analysis_gid)

    log("\n=== dev phase (full · analysis dependency seam) ===")
    dev_workers = run_dev_phase(dev_gid, analysis_gid)

    write_report(
        epic_gid=epic_gid,
        analysis_gid=analysis_gid,
        dev_gid=dev_gid,
        analysis_workers=analysis_workers,
        dev_workers=dev_workers,
        command=" ".join(sys.argv),
    )
    log("\nDONE.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as e:
        log(f"ERROR: {e}")
        raise SystemExit(1)
