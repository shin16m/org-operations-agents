#!/usr/bin/env python3
"""Create [fix] (and optional [re-review]) Asana subtasks from a failed review Result JSON.

Usage:
  python tools/pm_create_fix_subtask.py --parent <GID> --review-json path/to/review.json -y
  python tools/pm_create_fix_subtask.py --parent <GID> --review-json review.json --with-rereview -y
  python tools/pm_create_fix_subtask.py --parent <GID> --rereview-only --review-json review.json --round 2 -y
  python tools/pm_create_fix_subtask.py --parent <GID> --review-json review.json --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ASANA = ROOT / "skills/platform/asana-buddy/optional"

R3_ESCALATION_MARKER = "fix_escalation: R3"
R3_FIX_TITLE_RE = re.compile(r"\[fix\].*\(R3\)", re.I)

DEPT_FROM_OUTPUT = {
    "development": "development",
    "ux": "ux",
    "analysis": "analysis",
}

ANALYSIS_REVIEW_KIND_FIX: dict[str, tuple[str, str, str]] = {
    "analytics_requirements": ("analytics-pm", "analysis-reviewer", "analytics_requirements"),
    "data_model": ("data-architect", "analysis-reviewer", "data_model"),
    "pipeline": ("data-engineer", "analysis-reviewer", "pipeline"),
    "data_quality": ("data-steward", "analysis-reviewer", "data_quality"),
    "analysis_insights": ("data-analyst", "analysis-reviewer", "analysis_insights"),
    "model_eval": ("data-scientist", "analysis-reviewer", "model_eval"),
    "production_deploy_gate": ("", "analysis-reviewer", "production_deploy_gate"),
    "deploy_verification": ("ml-engineer", "analysis-reviewer", "deploy_verification"),
}


def infer_department(review_path: Path) -> str | None:
    parts = review_path.as_posix().replace("\\", "/").split("/")
    for i, part in enumerate(parts):
        if part in ("output", "skills") and i + 1 < len(parts):
            return DEPT_FROM_OUTPUT.get(parts[i + 1])
    return None


def _rel_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def format_findings(findings: list[dict[str, Any]] | None) -> str:
    if not findings:
        return "（findings なし — summary を参照）"
    lines: list[str] = []
    for item in findings:
        sev = item.get("severity", "medium")
        msg = item.get("message", "").strip()
        if msg:
            lines.append(f"- [{sev}] {msg}")
    return "\n".join(lines) if lines else "（findings なし — summary を参照）"


def build_r3_escalation_comment(
    *,
    fix_round: int,
    gate_label: str,
    review_path: Path,
) -> str:
    return (
        f"## 依頼者向け — fix R{fix_round} エスカレーション\n\n"
        f"同一ゲート `{gate_label}` で修正ラウンド **R{fix_round}** に到達しました。\n"
        "L3b 自動 worker kick を停止します。依頼者判断をお願いします。\n\n"
        f"- review JSON: `{_rel_path(review_path)}`\n"
        "- SSOT: docs/design/pm-review-rework-ssot.md § fix ループ上限\n"
    )


def post_r3_escalation_if_needed(
    *,
    parent_gid: str,
    fix_round: int,
    gate_label: str,
    review_path: Path,
    token: str,
) -> None:
    if fix_round < 3:
        return
    if str(ASANA) not in sys.path:
        sys.path.insert(0, str(ASANA))
    from asana_program_common import console_safe, create_task_story  # noqa: WPS433

    body = build_r3_escalation_comment(
        fix_round=fix_round,
        gate_label=gate_label,
        review_path=review_path,
    )
    create_task_story(parent_gid, body, token)
    print(console_safe(f"R3_ESCALATION  parent={parent_gid}  round=R{fix_round}  gate={gate_label}"))


def pm_child_has_open_r3_fix(parent_gid: str, token: str) -> bool:
    """True when incomplete [fix] R3+ subs block automatic worker kick."""
    if str(ASANA) not in sys.path:
        sys.path.insert(0, str(ASANA))
    from asana_program_common import fetch_task, list_subtasks  # noqa: WPS433

    for sub in list_subtasks(parent_gid, token):
        if sub.get("completed"):
            continue
        name = str(sub.get("name") or "")
        if R3_FIX_TITLE_RE.search(name):
            return True
        gid = str(sub.get("gid") or "")
        notes = str(fetch_task(gid, token).get("notes") or "")
        if R3_ESCALATION_MARKER in notes:
            return True
    return False


def resolve_workers(
    review: dict[str, Any],
    department: str,
    *,
    fix_assignee: str | None = None,
) -> tuple[str, str, str, str | None]:
    """Return fix_worker, reviewer, gate_label, worker_mode_hint."""
    review_kind = str(review.get("review_kind", ""))
    fix_target = review.get("fix_target")

    if department == "development":
        if review_kind == "requirements":
            return "requirements-writer", "dev-reviewer", "requirements", None
        if review_kind == "design":
            return "tech-designer", "dev-reviewer", "design", None
        if review_kind == "code":
            return "developer", "dev-reviewer", "code", None
        if review_kind == "verification":
            return "developer", "qa-verifier", "verification", None
        if review_kind == "mismatch":
            if fix_target == "document":
                return "requirements-writer", "dev-reviewer", "mismatch", "mode=as-built-spec"
            if fix_target == "code":
                return "developer", "dev-reviewer", "mismatch", None
            raise ValueError("MismatchReviewResult requires fix_target document|code")

    if department == "ux":
        if review_kind == "ux_spec":
            return "ux-designer", "ux-reviewer", "ux_spec", None
        if review_kind == "ux_implementation":
            if fix_target == "ux_spec":
                return "ux-designer", "ux-reviewer", "ux_spec", None
            return "developer", "ux-reviewer", "ux_implementation", None

    if department == "analysis":
        row = ANALYSIS_REVIEW_KIND_FIX.get(review_kind)
        if not row:
            raise ValueError(f"Unknown analysis review_kind: {review_kind}")
        fix_worker, reviewer, gate = row
        if review_kind == "production_deploy_gate" and not fix_assignee:
            raise ValueError(
                "production_deploy_gate failed: pass --fix-assignee (analytics-pm decides worker)"
            )
        if fix_assignee:
            fix_worker = fix_assignee
        elif not fix_worker:
            raise ValueError(f"review_kind={review_kind}: pass --fix-assignee")
        return fix_worker, reviewer, gate, None

    raise ValueError(f"Unsupported department={department} review_kind={review_kind}")


def detect_round(parent_subtask_names: list[str], gate_label: str) -> int:
    pattern = re.compile(rf"\[fix\].*{re.escape(gate_label)}.*\(R(\d+)\)", re.I)
    rounds = [int(m.group(1)) for name in parent_subtask_names if (m := pattern.search(name))]
    return max(rounds, default=0) + 1


def build_fix_request_block(review: dict[str, Any], review_path: Path) -> str:
    lines = [
        f"- review JSON: `{_rel_path(review_path)}`",
        f"- status: {review.get('status')}",
        f"- review_kind: {review.get('review_kind')}",
        f"- summary: {review.get('summary', '').strip()}",
    ]
    if review.get("fix_target"):
        lines.append(f"- fix_target: {review['fix_target']}")
    if review.get("mismatch_summary"):
        lines.append(f"- mismatch_summary: {review['mismatch_summary']}")
    lines.append("")
    lines.append("### 指摘")
    lines.append(format_findings(review.get("findings")))
    return "\n".join(lines)


def default_done_when(department: str, gate_label: str, worker_mode: str | None) -> str:
    if worker_mode == "mode=as-built-spec":
        return (
            "事後詳細仕様が更新され、指摘が解消されている。"
            "旧版は output/development/_archive/ へ退避済み。"
        )
    if department == "ux":
        return "UX 成果物が更新され、指摘が解消されている。旧版は output/ux/_archive/ へ退避推奨。"
    if department == "analysis":
        return "分析成果物が更新され、指摘が解消されている。旧版は output/analysis/_archive/ へ退避推奨。"
    if gate_label == "verification":
        return "動作検証で指摘された問題が解消されている。"
    if gate_label in ("requirements", "design"):
        return f"{gate_label} 成果物が更新され、再 review を依頼できる状態。"
    return "指摘が解消され、再 review を依頼できる状態。"


def assemble_fix_notes(
    *,
    department: str,
    assignee: str,
    round_n: int,
    gate_label: str,
    review: dict[str, Any],
    review_path: Path,
    worker_mode: str | None,
    done_when: str | None,
) -> str:
    fix_block = build_fix_request_block(review, review_path)
    bg = f"Review NG に伴う修正（R{round_n}）。ゲート: {gate_label}。"
    summary_parts = ["## 修正依頼", fix_block]
    if round_n >= 3:
        summary_parts.append(R3_ESCALATION_MARKER)
    if worker_mode:
        summary_parts.insert(0, f"**{worker_mode}**")
    summary = "\n\n".join(summary_parts)
    dw = (done_when or default_done_when(department, gate_label, worker_mode)).strip()
    if str(ASANA) not in sys.path:
        sys.path.insert(0, str(ASANA))
    from asana_program_common import assemble_subtask_notes  # noqa: WPS433

    return assemble_subtask_notes(
        background=bg,
        summary=summary,
        done_when=dw,
        department=department,
        assignee=assignee,
        status="assigned",
    )


def assemble_rereview_notes(
    *,
    department: str,
    assignee: str,
    round_n: int,
    gate_label: str,
    review_path: Path,
    fix_gid: str | None,
) -> str:
    bg = f"修正 R{round_n - 1} 完了後の再 review（R{round_n}）。"
    summary_lines = [
        f"review_kind: {gate_label}",
        f"元 review JSON: `{_rel_path(review_path)}`",
    ]
    if fix_gid:
        summary_lines.append(f"修正サブ GID: {fix_gid}")
    summary = "\n".join(summary_lines)
    dw = f"Result JSON が passed または passed_with_notes。output/{department}/reviews/ に保存。"
    if str(ASANA) not in sys.path:
        sys.path.insert(0, str(ASANA))
    from asana_program_common import assemble_subtask_notes  # noqa: WPS433

    return assemble_subtask_notes(
        background=bg,
        summary=summary,
        done_when=dw,
        department=department,
        assignee=assignee,
        status="assigned",
    )


def fix_subtask_name(fix_worker: str, gate_label: str, round_n: int) -> str:
    return f"[fix] {fix_worker} — {gate_label} review findings (R{round_n})"


def rereview_subtask_name(reviewer: str, gate_label: str, round_n: int) -> str:
    return f"[re-review] {reviewer} — {gate_label} (R{round_n})"


def plan_fix_subtasks(
    *,
    review: dict[str, Any],
    review_path: Path,
    department: str,
    round_n: int | None,
    fix_assignee: str | None,
    with_rereview: bool,
    rereview_only: bool,
    existing_subtask_names: list[str] | None = None,
) -> dict[str, Any]:
    status = review.get("status")
    if status not in ("failed",) and not rereview_only:
        raise ValueError(
            f"Review status is {status!r}; only 'failed' creates [fix] subs (use --rereview-only after fix)"
        )

    fix_worker, reviewer, gate_label, worker_mode = resolve_workers(
        review, department, fix_assignee=fix_assignee
    )
    names = existing_subtask_names or []
    fix_round = round_n or detect_round(names, gate_label)
    rereview_round = fix_round + 1

    items: list[dict[str, Any]] = []
    if not rereview_only:
        items.append(
            {
                "kind": "fix",
                "name": fix_subtask_name(fix_worker, gate_label, fix_round),
                "assignee": fix_worker,
                "notes": assemble_fix_notes(
                    department=department,
                    assignee=fix_worker,
                    round_n=fix_round,
                    gate_label=gate_label,
                    review=review,
                    review_path=review_path,
                    worker_mode=worker_mode,
                    done_when=None,
                ),
            }
        )
    if with_rereview or rereview_only:
        items.append(
            {
                "kind": "re-review",
                "name": rereview_subtask_name(reviewer, gate_label, rereview_round),
                "assignee": reviewer,
                "notes": assemble_rereview_notes(
                    department=department,
                    assignee=reviewer,
                    round_n=rereview_round,
                    gate_label=gate_label,
                    review_path=review_path,
                    fix_gid=None,
                ),
            }
        )

    return {
        "department": department,
        "gate_label": gate_label,
        "fix_round": fix_round,
        "rereview_round": rereview_round if (with_rereview or rereview_only) else None,
        "items": items,
    }


def _fetch_subtask_names(parent: str) -> list[str]:
    import subprocess

    py = ROOT / ".venv/Scripts/python.exe"
    if not py.is_file():
        py = Path(sys.executable)
    r = subprocess.run(
        [str(py), str(ASANA / "fetch_task.py"), "--gid", parent, "--list-subtasks"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**dict(__import__("os").environ), "PYTHONIOENCODING": "utf-8"},
    )
    if r.returncode != 0:
        return []
    names: list[str] = []
    for line in r.stdout.splitlines():
        m = re.match(r"\[[ x]\]\s+\d+\s+(.+)$", line.strip())
        if m:
            names.append(m.group(1).strip())
    return names


def _emit_dispatch(department: str, parent_gid: str, sub_gid: str, worker: str) -> None:
    if str(ROOT / "tools") not in sys.path:
        sys.path.insert(0, str(ROOT / "tools"))
    from pm_emit_worker_prompt import emit_snippet  # noqa: WPS433

    print(
        emit_snippet(
            department=department,
            parent_gid=parent_gid,
            sub_gid=sub_gid,
            worker_slug=worker,
        )
    )


def main() -> int:
    p = argparse.ArgumentParser(description="PM: create [fix] / [re-review] subtasks from review JSON")
    p.add_argument("--parent", required=True, help="PM child task GID (parent of new subs)")
    p.add_argument("--review-json", required=True, type=Path, help="Failed review Result JSON path")
    p.add_argument(
        "--department",
        choices=sorted(DEPT_FROM_OUTPUT.values()),
        help="Auto from output/<dept>/ if omitted",
    )
    p.add_argument("--round", type=int, help="Fix round R{n} (default: auto from existing [fix] subs)")
    p.add_argument("--fix-assignee", help="Override fix worker (required for some analysis gates)")
    p.add_argument(
        "--with-rereview",
        action="store_true",
        help="Also create [re-review] sub now (default: fix only; SSOT prefers after fix complete)",
    )
    p.add_argument("--rereview-only", action="store_true", help="Create [re-review] only (after fix complete)")
    p.add_argument("--emit-dispatch", action="store_true", help="Print WorkerDispatchSnippet for fix sub")
    p.add_argument("--dry-run", action="store_true", help="Print plan JSON only; no Asana writes")
    p.add_argument("-y", "--yes", action="store_true")
    args = p.parse_args()

    review_path = args.review_json
    if not review_path.is_file():
        print(f"Review file not found: {review_path}", file=sys.stderr)
        return 1

    review = json.loads(review_path.read_text(encoding="utf-8"))
    department = args.department or infer_department(review_path)
    if not department:
        print("Could not infer department; pass --department", file=sys.stderr)
        return 1

    existing_names: list[str] | None = None
    if args.round is None and not args.dry_run:
        existing_names = _fetch_subtask_names(args.parent)

    try:
        plan = plan_fix_subtasks(
            review=review,
            review_path=review_path,
            department=department,
            round_n=args.round,
            fix_assignee=args.fix_assignee,
            with_rereview=args.with_rereview,
            rereview_only=args.rereview_only,
            existing_subtask_names=existing_names,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.dry_run:
        dry = {
            "department": plan["department"],
            "gate_label": plan["gate_label"],
            "fix_round": plan["fix_round"],
            "rereview_round": plan["rereview_round"],
            "items": [
                {"kind": i["kind"], "name": i["name"], "assignee": i["assignee"]} for i in plan["items"]
            ],
        }
        print(json.dumps(dry, ensure_ascii=False, indent=2))
        return 0

    if not args.yes:
        print(f"Parent: {args.parent}")
        for item in plan["items"]:
            print(f"  + {item['name']} → {item['assignee']}")
        if input("Create subtasks? [y/N]: ").strip().lower() != "y":
            print("Cancelled.")
            return 0

    if str(ASANA) not in sys.path:
        sys.path.insert(0, str(ASANA))
    from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: WPS433
    from asana_program_common import console_safe, create_subtask, update_task_notes  # noqa: WPS433

    load_env_from_dotfile()
    token = get_token()

    created: list[dict[str, Any]] = []
    fix_gid: str | None = None
    for item in reversed(plan["items"]):
        sub = create_subtask(args.parent, item["name"], item["notes"], token)
        rec = {"kind": item["kind"], "gid": sub["gid"], "name": item["name"], "assignee": item["assignee"]}
        created.append(rec)
        if item["kind"] == "fix":
            fix_gid = sub["gid"]
        print(console_safe(f"  + {sub['gid']}  {item['name']}  → {item['assignee']}"))

    if fix_gid:
        for rec in created:
            if rec["kind"] == "re-review":
                notes = assemble_rereview_notes(
                    department=department,
                    assignee=rec["assignee"],
                    round_n=plan["rereview_round"],
                    gate_label=plan["gate_label"],
                    review_path=review_path,
                    fix_gid=fix_gid,
                )
                update_task_notes(rec["gid"], notes, token)

    if plan["fix_round"] >= 3:
        post_r3_escalation_if_needed(
            parent_gid=args.parent,
            fix_round=plan["fix_round"],
            gate_label=plan["gate_label"],
            review_path=review_path,
            token=token,
        )

    out = {
        "parent_gid": args.parent,
        "department": department,
        "fix_round": plan["fix_round"],
        "created": list(reversed(created)),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

    if args.emit_dispatch and fix_gid:
        fix_item = next(c for c in created if c["kind"] == "fix")
        print("--- WorkerDispatch (fix sub) ---")
        _emit_dispatch(department, args.parent, fix_gid, fix_item["assignee"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
