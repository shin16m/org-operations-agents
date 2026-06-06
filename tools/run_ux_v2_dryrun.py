#!/usr/bin/env python3
"""UX delivery v2 dryrun: bootstrap → ux-pm assign (v2 plan) → all workers comment+complete.

Record: docs/verification/ux-delivery-v2-dryrun.md

Usage (repo root):
  python tools/run_ux_v2_dryrun.py
  python tools/run_ux_v2_dryrun.py --ux-child <GID>
  python tools/run_ux_v2_dryrun.py --parent <EPIC_GID>
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

BOOTSTRAP = ROOT / "docs/verification/fixtures/planning/handoff/bootstrap.ux-v2-dryrun.json"
ASSIGN_PLAN = ROOT / "skills/ux/examples/assign-plan.dryrun-v2.json"
PM_SLUG = "ux-pm"

AGENT_SKILLS: dict[str, str] = {
    "task-dispatcher": "skills/platform/task-dispatcher/SKILL.md",
    "ux-pm": "skills/ux/ux-pm/SKILL.md",
    "ux-designer": "skills/ux/ux-designer/SKILL.md",
    "design-system-owner": "skills/ux/design-system-owner/SKILL.md",
    "ux-reviewer": "skills/ux/ux-reviewer/SKILL.md",
}

EXPECTED_WORKERS = ("ux-designer", "ux-reviewer", "design-system-owner", "ux-reviewer")
FIGMA_UI_STUB = "https://www.figma.com/design/dryrun-ux-v2-ui"
FIGMA_DS_STUB = "https://www.figma.com/design/dryrun-ux-v2-ds"


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


def find_ux_child(epic_gid: str) -> str | None:
    for gid, name, _ in list_subtask_gids(epic_gid):
        low = name.lower()
        if "ux" in low or "体験" in name:
            return gid
    return None


def bootstrap_epic() -> tuple[str, str]:
    r = _run(_py("handoff_to_asana.py", "--handoff", str(BOOTSTRAP.relative_to(ROOT)), "-y"))
    log(r.stdout)
    m = re.search(r"created_parent\s+(\d+)(?:\s+(https://\S+))?", r.stdout)
    if not m:
        raise RuntimeError("bootstrap did not return created_parent GID")
    epic_gid = m.group(1)
    ux_child = find_ux_child(epic_gid)
    if not ux_child:
        raise RuntimeError("UX child not found under bootstrapped epic")
    return epic_gid, ux_child


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
            "ux",
            "--update-parent-assignee",
            PM_SLUG,
            "-y",
        ]
    )
    log(r.stdout)
    if r.returncode != 0:
        raise RuntimeError(f"pm_assign_subtasks failed\n{r.stderr or r.stdout}")


def write_stub_artifacts(parent_gid: str) -> list[str]:
    stub_dir = ROOT / "output/dryrun/ux"
    stub_dir.mkdir(parents=True, exist_ok=True)
    spec = stub_dir / f"{parent_gid}-ux-spec.md"
    ds = stub_dir / f"{parent_gid}-design-system.md"
    spec.write_text(
        f"# UX spec dryrun stub\n\nFigma UI: {FIGMA_UI_STUB}\n",
        encoding="utf-8",
    )
    ds.write_text(
        f"# Design System dryrun stub\n\nFigma DS: {FIGMA_DS_STUB}\n",
        encoding="utf-8",
    )
    reviews = ROOT / "output/ux/reviews"
    reviews.mkdir(parents=True, exist_ok=True)
    for name in ("design-quality-review", "ux-spec-review"):
        p = reviews / f"{parent_gid}-{name}.json"
        p.write_text(
            json.dumps(
                {
                    "schema_version": "1.1",
                    "status": "passed_with_notes",
                    "summary": f"ux v2 dryrun stub — {name}",
                    "review_kind": "design_quality" if "quality" in name else "ux_spec",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return [
        str(spec.relative_to(ROOT)),
        str(ds.relative_to(ROOT)),
        FIGMA_UI_STUB,
        FIGMA_DS_STUB,
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
            f"ux v2 dryrun — {assignee}",
            agent_comment_body(
                actions=[
                    f"サブタスク `{name}` の done_when を ux v2 dryrun で充足",
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
    if len(assignees) != 4:
        raise RuntimeError(f"expected 4 worker subtasks, got {len(assignees)}: {assignees}")
    if "design-system-owner" not in assignees:
        raise RuntimeError("design-system-owner subtask missing")
    return assignees


def write_report(
    *,
    epic_gid: str,
    ux_gid: str,
    workers: list[str],
    artifacts: list[str],
    epic_url: str = "",
    command: str,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# UX delivery v2 — dry-run 実行記録",
        "",
        f"実施: {now}",
        "",
        "## 目的",
        "",
        "`ux-delivery` v2（profile: flagship）の PM サブタスク分解・"
        "**ux-designer / design-system-owner / ux-reviewer（design_quality + ux_spec）** が "
        "`comment_task` → `complete_task` まで到達することを Asana 上で確認する。",
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
        f"| UX 子 GID | `{ux_gid}` |",
    ]
    if epic_url:
        lines.append(f"| 親 URL | {epic_url} |")
    lines.extend(
        [
            "",
            "## 結果",
            "",
            f"- workers（順）: {', '.join(workers)}",
            f"- 期待ロール: {', '.join(EXPECTED_WORKERS)}",
            "- サブタスク数: 4",
            "- design-system-owner: 到達確認",
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
            "- [x] ux-pm が assign-plan.dryrun-v2.json でサブタスク分解",
            "- [x] design-system-owner サブが存在",
            "- [x] 各ワーカーが comment_task → complete",
            "- [x] ux-pm が親を complete",
            "- [x] stub に Figma URL を含む",
            "",
            "## 関連",
            "",
            "- [`ux-delivery-io.md`](../design/ux-delivery-io.md)",
            "- [`ux-pm-assignment.md`](../design/ux-pm-assignment.md)",
            "- [`run_ux_v2_dryrun.py`](../../tools/run_ux_v2_dryrun.py)",
            "- 索引: [`docs/verification/README.md`](README.md)",
            "",
        ]
    )
    out = ROOT / "docs/verification/ux-delivery-v2-dryrun.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    log(f"\nReport: {out}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--parent", help="Existing epic GID (find UX child under it)")
    p.add_argument("--ux-child", help="Existing UX child GID (skip bootstrap)")
    args = p.parse_args()

    epic_url = ""
    if args.ux_child:
        ux_gid = args.ux_child
        epic_gid = args.parent or ux_gid
    elif args.parent:
        epic_gid = args.parent
        ux_gid = find_ux_child(epic_gid)
        if not ux_gid:
            raise SystemExit(f"No UX child under epic {epic_gid}")
    else:
        log("=== bootstrap ===")
        epic_gid, ux_gid = bootstrap_epic()

    log(f"Epic GID: {epic_gid}")
    log(f"UX child GID: {ux_gid}")

    log("\n=== dispatch ===")
    comment_and_complete(
        ux_gid,
        "task-dispatcher",
        "dispatch → ux-pm",
        agent_comment_body(
            actions=[
                "DispatchRequest（department=ux）を解決",
                "entry_agent ux-pm 向け dryrun を開始",
            ],
        ),
    )
    _run(_py("complete_task.py", "--gid", ux_gid, "--undo", "-y"))

    log("\n=== pm_assign (v2) ===")
    pm_assign(ux_gid)

    log("\n=== verify subtasks ===")
    verify_subtasks(ux_gid)

    log("\n=== workers ===")
    workers = run_workers(ux_gid)

    artifacts = write_stub_artifacts(ux_gid)

    log("\n=== ux-pm complete ===")
    comment_and_complete(
        ux_gid,
        PM_SLUG,
        "ux-pm — DeptWorkComplete (v2 dryrun)",
        agent_comment_body(
            actions=[
                "ux-delivery v2 全ワーカーサブを完了集約",
                "DeptWorkComplete.artifacts[] に Figma URL + stub パスを記載",
            ],
            artifacts=artifacts,
        ),
    )

    write_report(
        epic_gid=epic_gid,
        ux_gid=ux_gid,
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
