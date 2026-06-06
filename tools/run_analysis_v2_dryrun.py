#!/usr/bin/env python3
"""Analysis delivery v2 dryrun: bootstrap → analytics-pm assign → all workers comment+complete.

Record: docs/verification/analysis/analysis-delivery-v2-dryrun.md

Usage (repo root):
  python tools/run_analysis_v2_dryrun.py
  python tools/run_analysis_v2_dryrun.py --analysis-child <GID>
  python tools/run_analysis_v2_dryrun.py --parent <EPIC_GID>
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
ASSIGN_PLAN = ROOT / "skills/analysis/examples/assign-plan.dryrun-v2.json"
PM_SLUG = "analytics-pm"

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

# assign-plan.dryrun-v2.json worker assignees in workflow order
EXPECTED_WORKER_COUNT = 10
API_STUB = "https://api.example.com/dryrun/analysis/v1/predict"


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


def list_subtask_gids(parent_gid: str) -> list[tuple[str, str, bool]]:
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
    for gid, name, _ in list_subtask_gids(epic_gid):
        low = name.lower()
        if "分析" in name or "analysis" in low:
            return gid
    return None


def bootstrap_epic() -> tuple[str, str]:
    r = _run(
        _py(
            "handoff_to_asana.py",
            "--handoff",
            str(BOOTSTRAP.relative_to(ROOT)),
            "-y",
        )
    )
    log(r.stdout)
    m = re.search(r"created_parent\s+(\d+)(?:\s+(https://\S+))?", r.stdout)
    if not m:
        raise RuntimeError("bootstrap did not return created_parent GID")
    epic_gid = m.group(1)
    child = find_analysis_child(epic_gid)
    if not child:
        raise RuntimeError("analysis child not found under bootstrapped epic")
    return epic_gid, child


def pm_assign(parent_gid: str) -> None:
    r = _run(
        [
            str(PY),
            str(ASANA / "pm_assign_subtasks.py"),
            "--parent",
            parent_gid,
            "--plan",
            str(ASSIGN_PLAN),
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


def write_stub_artifacts(parent_gid: str) -> list[str]:
    stub_dir = ROOT / "output/dryrun/analysis"
    stub_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "requirements": stub_dir / f"{parent_gid}-requirements.md",
        "release": stub_dir / f"{parent_gid}-release.md",
        "catalog": stub_dir / f"{parent_gid}-catalog.md",
        "model": stub_dir / f"{parent_gid}-model-stub.md",
    }
    paths["requirements"].write_text(
        "# Analysis requirements dryrun stub\n\nKPI: dryrun\n",
        encoding="utf-8",
    )
    paths["release"].write_text(
        f"# Release dryrun stub\n\nAPI: {API_STUB}\n",
        encoding="utf-8",
    )
    paths["catalog"].write_text(
        "# Catalog dryrun stub\n\nSLA: daily · lag max 2h\n",
        encoding="utf-8",
    )
    paths["model"].write_text("# Model card dryrun stub\n", encoding="utf-8")
    reviews = ROOT / "output/analysis/reviews"
    reviews.mkdir(parents=True, exist_ok=True)
    (reviews / f"{parent_gid}-dryrun-review.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "status": "passed_with_notes",
                "summary": "analysis v2 dryrun stub review",
                "review_kind": "data_model",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return [
        str(paths["requirements"].relative_to(ROOT)),
        str(paths["catalog"].relative_to(ROOT)),
        str(paths["model"].relative_to(ROOT)),
        API_STUB,
    ]


def run_workers(parent_gid: str) -> list[str]:
    worked: list[str] = []
    for gid, name, done in list_subtask_gids(parent_gid):
        if done:
            continue
        assignee = fetch_assignee(gid)
        if not assignee or assignee == PM_SLUG:
            continue
        comment_and_complete(
            gid,
            assignee,
            f"analysis v2 dryrun — {assignee}",
            agent_comment_body(
                actions=[
                    f"サブタスク `{name}` の done_when を analysis v2 dryrun で充足",
                    f"{assignee} が署名付き comment_task を投稿",
                ],
                artifacts=[f"Asana subtask GID {gid}"],
            ),
        )
        worked.append(assignee)
        log(f"  worker OK  {assignee}  →  {gid}")
    return worked


def verify_subtasks(parent_gid: str) -> list[str]:
    assignees: list[str] = []
    for gid, name, _ in list_subtask_gids(parent_gid):
        a = fetch_assignee(gid)
        if a and a != PM_SLUG:
            assignees.append(a)
            log(f"  sub {gid}  {name}  →  {a}")
    if len(assignees) != EXPECTED_WORKER_COUNT:
        raise RuntimeError(
            f"expected {EXPECTED_WORKER_COUNT} worker subtasks, got {len(assignees)}: {assignees}"
        )
    if "analytics-requirements-writer" not in assignees:
        raise RuntimeError("analytics-requirements-writer subtask missing (PM separation)")
    if assignees.count("analytics-requirements-writer") < 2:
        raise RuntimeError("expected requirements + release subtasks for analytics-requirements-writer")
    return assignees


def write_report(
    *,
    epic_gid: str,
    analysis_gid: str,
    workers: list[str],
    artifacts: list[str],
    epic_url: str = "",
    command: str,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Analysis delivery v2 — dry-run 実行記録",
        "",
        f"実施: {now}",
        "",
        "## 目的",
        "",
        "`analysis-delivery` v2（profile: full）の PM サブタスク分解・"
        "**analytics-requirements-writer** 含む全ワーカーが "
        "`comment_task` → `complete_task` まで到達することを Asana 上で確認する。",
        "",
        "> **API URL:** dryrun 用 stub（`api.example.com`）は実在しません。"
        " 下流 consume 契約の形式確認用です。",
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
        f"| assign plan | `{ASSIGN_PLAN.relative_to(ROOT).as_posix()}` |",
        "",
        "## Asana",
        "",
        "| 項目 | 値 |",
        "|------|-----|",
        f"| 親エピック GID | `{epic_gid}` |",
        f"| 分析子 GID | `{analysis_gid}` |",
    ]
    if epic_url:
        lines.append(f"| 親 URL | {epic_url} |")
    lines.extend(
        [
            "",
            "## 結果",
            "",
            f"- workers（順）: {', '.join(workers)}",
            f"- サブタスク数: {EXPECTED_WORKER_COUNT}",
            "- analytics-requirements-writer: 要件 + リリースの 2 サブ到達",
            "",
            "## stub 成果物",
            "",
        ]
    )
    for a in artifacts:
        lines.append(f"- `{a}`")
    lines.extend(
        [
            "",
            "## チェックリスト",
            "",
            "- [x] analytics-pm が assign-plan.dryrun-v2.json でサブタスク分解",
            "- [x] analytics-requirements-writer サブが存在（PM 分離）",
            "- [x] 各ワーカーが comment_task → complete",
            "- [x] analytics-pm が親を complete",
            "- [x] stub に API URL を含む（下流 bridge 形式）",
            "",
            "## 手動実行",
            "",
            "```powershell",
            "python tools/run_analysis_v2_dryrun.py",
            "python tools/run_analysis_v2_dryrun.py --analysis-child <GID> --parent <EPIC_GID>",
            "```",
            "",
            "## 関連",
            "",
            "- [`analysis-delivery-io.md`](../design/analysis-delivery-io.md)",
            "- [`analytics-pm-assignment.md`](../design/analytics-pm-assignment.md)",
            "- [`cross-team-artifact-bridge.md`](../design/cross-team-artifact-bridge.md)",
            "- [`run_analysis_v2_dryrun.py`](../../tools/run_analysis_v2_dryrun.py)",
            "",
        ]
    )
    out = ROOT / "docs/verification/analysis/analysis-delivery-v2-dryrun.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    log(f"\nReport: {out}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--parent", help="Existing epic GID")
    p.add_argument("--analysis-child", help="Existing analysis child GID")
    args = p.parse_args()

    epic_url = ""
    if args.analysis_child:
        analysis_gid = args.analysis_child
        epic_gid = args.parent or analysis_gid
    elif args.parent:
        epic_gid = args.parent
        analysis_gid = find_analysis_child(epic_gid)
        if not analysis_gid:
            raise SystemExit(f"No analysis child under epic {epic_gid}")
    else:
        log("=== bootstrap ===")
        epic_gid, analysis_gid = bootstrap_epic()

    log(f"Epic GID: {epic_gid}")
    log(f"Analysis child GID: {analysis_gid}")

    log("\n=== dispatch ===")
    comment_and_complete(
        analysis_gid,
        "task-dispatcher",
        "dispatch → analytics-pm",
        agent_comment_body(
            actions=[
                "DispatchRequest（department=analysis）を解決",
                "entry_agent analytics-pm 向け dryrun を開始",
            ],
        ),
    )
    _run(_py("complete_task.py", "--gid", analysis_gid, "--undo", "-y"))

    log("\n=== pm_assign (v2) ===")
    pm_assign(analysis_gid)

    log("\n=== verify subtasks ===")
    verify_subtasks(analysis_gid)

    log("\n=== workers ===")
    workers = run_workers(analysis_gid)

    artifacts = write_stub_artifacts(analysis_gid)

    log("\n=== analytics-pm complete ===")
    comment_and_complete(
        analysis_gid,
        PM_SLUG,
        "analytics-pm — DeptWorkComplete (v2 dryrun)",
        agent_comment_body(
            actions=[
                "analysis-delivery v2 全ワーカーサブを完了集約",
                "DeptWorkComplete.artifacts[] にカタログ・API stub を記載",
            ],
            artifacts=artifacts,
        ),
    )

    write_report(
        epic_gid=epic_gid,
        analysis_gid=analysis_gid,
        workers=workers,
        artifacts=artifacts,
        epic_url=epic_url,
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
