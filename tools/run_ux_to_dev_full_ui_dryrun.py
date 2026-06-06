#!/usr/bin/env python3
"""UX → development full-ui seam dryrun: UX v2 complete → ## 依存 transfer → dev full-ui.

Record: docs/verification/cross-team/ux-to-dev-full-ui-dryrun.md

Usage (repo root):
  python tools/run_ux_to_dev_full_ui_dryrun.py
  python tools/run_ux_to_dev_full_ui_dryrun.py --parent <EPIC_GID>
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

BOOTSTRAP = ROOT / "docs/verification/fixtures/planning/handoff/bootstrap.ux-to-dev-full-ui-dryrun.json"
UX_PLAN = ROOT / "skills/ux/examples/assign-plan.dryrun-v2.json"
DEV_PLAN = ROOT / "skills/development/examples/assign-plan.full-ui-v1.json"
UX_PM = "ux-pm"
DEV_PM = "product-manager"

FIGMA_UI = "https://www.figma.com/design/dryrun-ux-to-dev-ui"
FIGMA_DS = "https://www.figma.com/design/dryrun-ux-to-dev-ds"

AGENT_SKILLS: dict[str, str] = {
    "task-dispatcher": "skills/platform/task-dispatcher/SKILL.md",
    "ux-pm": "skills/ux/ux-pm/SKILL.md",
    "ux-designer": "skills/ux/ux-designer/SKILL.md",
    "design-system-owner": "skills/ux/design-system-owner/SKILL.md",
    "ux-reviewer": "skills/ux/ux-reviewer/SKILL.md",
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


def find_child(epic_gid: str, *, ux: bool) -> str | None:
    for gid, name, _ in list_subtasks(epic_gid):
        low = name.lower()
        if ux and ("ux" in low or "体験" in name):
            return gid
        if not ux and ("開発" in name or "development" in low or "full-ui" in low):
            return gid
    return None


def bootstrap_epic() -> tuple[str, str, str]:
    r = _run(_py("handoff_to_asana.py", "--handoff", str(BOOTSTRAP.relative_to(ROOT)), "-y"))
    log(r.stdout)
    m = re.search(r"created_parent\s+(\d+)", r.stdout)
    if not m:
        raise RuntimeError("bootstrap did not return created_parent GID")
    epic_gid = m.group(1)
    ux_gid = find_child(epic_gid, ux=True)
    dev_gid = find_child(epic_gid, ux=False)
    if not ux_gid or not dev_gid:
        raise RuntimeError(f"children missing under epic {epic_gid}: ux={ux_gid} dev={dev_gid}")
    return epic_gid, ux_gid, dev_gid


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
            f"ux-to-dev dryrun — {assignee}",
            agent_comment_body(
                actions=[f"サブタスク `{name}` dryrun 完了", f"{assignee} comment_task"],
                artifacts=[f"Asana subtask GID {gid}"],
            ),
        )
        worked.append(assignee)
        log(f"  worker OK  {assignee}  →  {gid}")
    return worked


def write_ux_stubs(ux_gid: str) -> list[str]:
    stub_dir = ROOT / "output/dryrun/ux"
    stub_dir.mkdir(parents=True, exist_ok=True)
    spec = stub_dir / f"{ux_gid}-ux-spec.md"
    ds = stub_dir / f"{ux_gid}-design-system.md"
    spec.write_text(f"# UX spec dryrun\n\nFigma UI: {FIGMA_UI}\n", encoding="utf-8")
    ds.write_text(f"# Design System dryrun\n\nFigma DS: {FIGMA_DS}\n", encoding="utf-8")
    reviews = ROOT / "output/ux/reviews"
    reviews.mkdir(parents=True, exist_ok=True)
    for kind, review_kind in (("design-quality-review", "design_quality"), ("ux-spec-review", "ux_spec")):
        p = reviews / f"{ux_gid}-{kind}.json"
        p.write_text(
            json.dumps(
                {"schema_version": "1.1", "status": "passed_with_notes", "review_kind": review_kind},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return [spec.relative_to(ROOT).as_posix(), ds.relative_to(ROOT).as_posix(), FIGMA_UI, FIGMA_DS]


def transfer_ux_dependency(dev_gid: str, ux_gid: str) -> None:
    from agent_handler_asana import get_token, load_env_from_dotfile
    from asana_program_common import fetch_task, update_task_notes

    write_ux_stubs(ux_gid)
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
        f"チーム: development\n\nprofile: full-ui\n担当: {DEV_PM}\n状態: in_progress\n\n"
        f"{body}\n\n"
        f"## 依存（読み取り専用）\n\n"
        f"| 種別 | 参照 | バージョン | 提供チーム |\n"
        f"|------|------|------------|------------|\n"
        f"| UX 仕様 | output/dryrun/ux/{ux_gid}-ux-spec.md | dryrun | ux |\n"
        f"| Figma UI | {FIGMA_UI} | dryrun | ux |\n"
        f"| Design System | output/dryrun/ux/{ux_gid}-design-system.md | dryrun | ux |\n"
        f"| Figma DS | {FIGMA_DS} | dryrun | ux |\n"
    )
    update_task_notes(dev_gid, notes.strip(), token)
    log(f"  dev notes updated with UX ## 依存 ({dev_gid})")


def verify_dev_dependency(dev_gid: str, ux_gid: str) -> None:
    notes = fetch_notes(dev_gid)
    required = [
        "## 依存（読み取り専用）",
        f"output/dryrun/ux/{ux_gid}-ux-spec.md",
        FIGMA_UI,
        FIGMA_DS,
        "profile: full-ui",
    ]
    missing = [r for r in required if r not in notes]
    if missing:
        raise RuntimeError(f"dev dependency verification failed — missing: {missing}")
    if "## 依存" in notes and notes.index("## 依存") < notes.find("profile: full-ui"):
        raise RuntimeError("## 依存 must appear after profile header block")
    log("  verify OK — dev notes contain ## 依存 + Figma URLs")


def run_ux_phase(ux_gid: str) -> list[str]:
    comment_and_complete(
        ux_gid,
        "task-dispatcher",
        "dispatch → ux-pm",
        agent_comment_body(actions=["UX→dev dryrun dispatch"]),
    )
    _run(_py("complete_task.py", "--gid", ux_gid, "--undo", "-y"))
    pm_assign(ux_gid, UX_PLAN, "ux", UX_PM)
    workers = run_workers(ux_gid, UX_PM)
    artifacts = write_ux_stubs(ux_gid)
    comment_and_complete(
        ux_gid,
        UX_PM,
        "ux-pm — DeptWorkComplete",
        agent_comment_body(
            actions=["UX v2 完了 · Figma URL を artifacts に公開"],
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


def run_dev_phase(dev_gid: str, ux_gid: str) -> list[str]:
    assignee = fetch_assignee(dev_gid)
    if assignee != DEV_PM:
        comment_and_complete(
            dev_gid,
            "task-dispatcher",
            "dispatch → product-manager",
            agent_comment_body(
                actions=[
                    "DispatchRequest（department=development）を解決",
                    "UX 子完了を前提に product-manager へ委譲",
                ],
            ),
        )
        _run(_py("complete_task.py", "--gid", dev_gid, "--undo", "-y"))

    transfer_ux_dependency(dev_gid, ux_gid)
    verify_dev_dependency(dev_gid, ux_gid)

    if not has_worker_subtasks(dev_gid, DEV_PM):
        pm_assign(dev_gid, DEV_PLAN, "development", DEV_PM)
    else:
        log("  pm_assign skipped — worker subtasks already exist")
    workers = run_workers(dev_gid, DEV_PM)
    comment_and_complete(
        dev_gid,
        DEV_PM,
        "product-manager — DeptWorkComplete (full-ui dryrun)",
        agent_comment_body(
            actions=["full-ui 全ワーカー完了 · UX 依存を read-only で consume"],
            artifacts=[f"UX child {ux_gid}", FIGMA_UI],
        ),
    )
    return workers


def write_report(
    *,
    epic_gid: str,
    ux_gid: str,
    dev_gid: str,
    ux_workers: list[str],
    dev_workers: list[str],
    command: str,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# UX → development full-ui — 継ぎ目 dryrun",
        "",
        f"実施: {now}",
        "",
        "## 目的",
        "",
        "UX 子単体ではなく、**UX 完了 → product-manager が `## 依存` 転記 → full-ui 着手**"
        "までのチーム間継ぎ目を Asana 上で確認する。",
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
        f"| UX assign plan | `{UX_PLAN.relative_to(ROOT).as_posix()}` |",
        f"| dev assign plan | `{DEV_PLAN.relative_to(ROOT).as_posix()}` |",
        "",
        "## Asana",
        "",
        "| 項目 | GID |",
        "|------|-----|",
        f"| 親エピック | `{epic_gid}` |",
        f"| UX 子 | `{ux_gid}` |",
        f"| 開発子（full-ui） | `{dev_gid}` |",
        "",
        "## 継ぎ目チェック",
        "",
        "- [x] UX 子: ux-pm が v2 全ワーカー完了 · Figma stub を artifacts に含む",
        "- [x] 開発子: `## 依存（読み取り専用）` に UX 仕様パス + Figma URL が転記されている",
        "- [x] 開発子: `profile: full-ui` ヘッダのあとに依存表",
        f"- [x] Figma UI stub: `{FIGMA_UI}`（実在ファイルではない）",
        "- [x] product-manager が pm_assign 後、full-ui ワーカーが comment → complete",
        "",
        "## 結果",
        "",
        f"- UX workers: {', '.join(ux_workers)}",
        f"- dev workers: {', '.join(dev_workers)}",
        "",
        "## 関連",
        "",
        "- [`cross-team-artifact-bridge.md`](../design/cross-team-artifact-bridge.md)",
        "- [`ux-delivery-v2-dryrun.md`](../ux/ux-delivery-v2-dryrun.md)",
        "- [`run_ux_to_dev_full_ui_dryrun.py`](../../tools/run_ux_to_dev_full_ui_dryrun.py)",
        "",
    ]
    out = ROOT / "docs/verification/cross-team/ux-to-dev-full-ui-dryrun.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    log(f"\nReport: {out}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--parent", help="Existing epic GID (find UX/dev children)")
    p.add_argument(
        "--from-dev",
        action="store_true",
        help="Skip UX phase (UX child already complete; requires --parent)",
    )
    args = p.parse_args()

    if args.from_dev and not args.parent:
        p.error("--from-dev requires --parent")

    if args.parent:
        epic_gid = args.parent
        ux_gid = find_child(epic_gid, ux=True)
        dev_gid = find_child(epic_gid, ux=False)
        if not ux_gid or not dev_gid:
            raise SystemExit(f"UX/dev children not found under {epic_gid}")
    else:
        log("=== bootstrap ===")
        epic_gid, ux_gid, dev_gid = bootstrap_epic()

    log(f"Epic: {epic_gid}  UX: {ux_gid}  dev: {dev_gid}")

    if args.from_dev:
        log("\n=== UX phase — skipped (--from-dev) ===")
        ux_workers = ["(skipped)"]
    else:
        log("\n=== UX phase (v2) ===")
        ux_workers = run_ux_phase(ux_gid)

    log("\n=== dev phase (full-ui · dependency seam) ===")
    dev_workers = run_dev_phase(dev_gid, ux_gid)

    write_report(
        epic_gid=epic_gid,
        ux_gid=ux_gid,
        dev_gid=dev_gid,
        ux_workers=ux_workers,
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
