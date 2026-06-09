#!/usr/bin/env python3
"""Evaluate milestone tracker readiness from a checklist fixture.

Usage:
  python tools/check_milestone_readiness.py --checklist docs/verification/fixtures/milestone-readiness/m5-learning-loop.json
  python tools/check_milestone_readiness.py --checklist ... --out output/governance/milestone-reports/report.json
  python tools/check_milestone_readiness.py --checklist ... --strict   # exit 1 if score < min_score_achieved
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / ".venv/Scripts/python.exe"
if not PY.is_file():
    PY = Path(sys.executable)


def _status_for_score(score: float, achieved: float, warn: float) -> str:
    if score >= achieved:
        return "achieved"
    if score >= warn:
        return "warn"
    return "not_achieved"


def _axis_scores(checks: list[dict[str, Any]]) -> dict[str, float]:
    axes = ("parts", "enforcement", "e2e")
    out: dict[str, float] = {}
    for axis in axes:
        weighted = 0.0
        total_w = 0.0
        for c in checks:
            if c.get("axis") != axis:
                continue
            w = float(c.get("weight") or 0)
            total_w += w
            if c.get("result") == "pass":
                weighted += w
        out[axis] = round(100.0 * weighted / total_w, 1) if total_w else 0.0
    return out


def _run_cli_help(target: str) -> tuple[bool, str]:
    path = ROOT / target
    if not path.is_file():
        return False, f"missing file: {target}"
    r = subprocess.run(
        [str(PY), str(path), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        detail = (r.stderr or r.stdout or "").strip()[:300]
        return False, detail or f"exit {r.returncode}"
    return True, "exit 0"


def _run_unittest(module_spec: str) -> tuple[bool, str]:
    modules = module_spec.split()
    cmd = [str(PY), "-m", "unittest", *modules, "-q"]
    r = subprocess.run(
        cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if r.returncode != 0:
        detail = (r.stderr or r.stdout or "").strip()[:400]
        return False, detail or f"exit {r.returncode}"
    return True, f"pass ({len(modules)} module(s))"


def _check_file_exists(target: str) -> tuple[bool, str]:
    path = ROOT / target
    if path.is_file():
        return True, "file exists"
    if path.is_dir():
        return True, "directory exists"
    return False, f"not found: {target}"


def _check_rg_pattern(target: str, pattern: str) -> tuple[bool, str]:
    base = ROOT / target
    if not base.exists():
        return False, f"path not found: {target}"
    flags = re.MULTILINE
    try:
        rx = re.compile(pattern, flags)
    except re.error as exc:
        return False, f"invalid pattern: {exc}"

    if base.is_file():
        text = base.read_text(encoding="utf-8", errors="replace")
        if rx.search(text):
            return True, f"match in {target}"
        return False, f"no match in {target}"

    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in {".pyc", ".png", ".jpg", ".woff", ".woff2"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if rx.search(text):
            rel = path.relative_to(ROOT).as_posix()
            return True, f"match in {rel}"
    return False, f"no match under {target}"


def _check_validate_script(target: str) -> tuple[bool, str]:
    path = ROOT / target
    if not path.is_file():
        return False, f"missing: {target}"
    r = subprocess.run(
        [str(PY), str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        detail = (r.stderr or r.stdout or "").strip()[:300]
        return False, detail or f"exit {r.returncode}"
    return True, "exit 0"


def _check_syntax(target: str) -> tuple[bool, str]:
    path = ROOT / target
    if not path.is_file():
        return False, f"missing file: {target}"
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return False, str(exc)
    return True, "syntax ok"


def run_check(item: dict[str, Any]) -> tuple[str, str]:
    ctype = item.get("check_type", "")
    target = str(item.get("target") or "")
    if ctype == "cli_help":
        if not target:
            return "skip", "no target"
        ok, detail = _run_cli_help(target)
        return ("pass" if ok else "fail"), detail
    if ctype == "unittest":
        mod = str(item.get("unittest_module") or target)
        if not mod:
            return "skip", "no unittest_module"
        ok, detail = _run_unittest(mod)
        return ("pass" if ok else "fail"), detail
    if ctype == "file_exists":
        if not target:
            return "skip", "no target"
        ok, detail = _check_file_exists(target)
        return ("pass" if ok else "fail"), detail
    if ctype == "rg_pattern":
        pattern = str(item.get("pattern") or "")
        if not target or not pattern:
            return "skip", "target/pattern required"
        ok, detail = _check_rg_pattern(target, pattern)
        return ("pass" if ok else "fail"), detail
    if ctype == "validate_script":
        if not target:
            return "skip", "no target"
        ok, detail = _check_validate_script(target)
        return ("pass" if ok else "fail"), detail
    if ctype == "manual_doc":
        return "skip", "manual verification required"
    return "skip", f"unknown check_type: {ctype}"


def evaluate_checklist(
    data: dict[str, Any],
    *,
    tracker_gid: str | None = None,
    work_epic_gid: str | None = None,
    checklist_path: str,
) -> dict[str, Any]:
    achieved = float(data.get("min_score_achieved", 80))
    warn = float(data.get("min_score_warn", 70))
    checks_out: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    follow_ups: list[dict[str, Any]] = []
    weighted = 0.0
    total_w = 0.0

    for item in data.get("checks", []):
        result, detail = run_check(item)
        w = float(item.get("weight") or 0)
        if result != "skip":
            total_w += w
            if result == "pass":
                weighted += w
        entry = {
            "id": item.get("id"),
            "description": item.get("description"),
            "check_type": item.get("check_type"),
            "weight": w,
            "axis": item.get("axis"),
            "result": result,
            "detail": detail,
        }
        checks_out.append(entry)
        if result == "fail":
            gaps.append(
                {
                    "check_id": item.get("id"),
                    "message": f"{item.get('description')}: {detail}",
                    "severity": item.get("severity_on_fail", "P2"),
                }
            )
            follow_ups.append(
                {
                    "title": f"Fix: {item.get('id')}",
                    "department": "development",
                    "summary": str(item.get("description") or ""),
                }
            )

    score = round(100.0 * weighted / total_w, 1) if total_w else 0.0
    report = {
        "schema_version": "1.0",
        "milestone_id": data.get("milestone_id"),
        "title": data.get("title"),
        "tracker_gid": tracker_gid,
        "work_epic_gid": work_epic_gid or data.get("work_epic_gid"),
        "score": score,
        "status": _status_for_score(score, achieved, warn),
        "checklist_path": checklist_path,
        "axis_scores": _axis_scores(checks_out),
        "checks": checks_out,
        "gaps": gaps,
        "follow_up_candidates": follow_ups,
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    }
    return report


def main() -> int:
    p = argparse.ArgumentParser(description="Milestone readiness checklist evaluator")
    p.add_argument("--checklist", required=True, help="Path to milestone-readiness JSON")
    p.add_argument("--tracker-gid", default=None)
    p.add_argument("--work-epic-gid", default=None)
    p.add_argument("--out", default=None, help="Write MilestoneEffectivenessReport JSON")
    p.add_argument("--strict", action="store_true", help="exit 1 if score < min_score_achieved")
    args = p.parse_args()

    checklist_path = Path(args.checklist)
    if not checklist_path.is_file():
        print(f"checklist not found: {checklist_path}", file=sys.stderr)
        return 2

    data = json.loads(checklist_path.read_text(encoding="utf-8"))
    rel = checklist_path.relative_to(ROOT).as_posix() if checklist_path.is_relative_to(ROOT) else str(checklist_path)
    report = evaluate_checklist(
        data,
        tracker_gid=args.tracker_gid,
        work_epic_gid=args.work_epic_gid,
        checklist_path=rel,
    )

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        out_path = ROOT / args.out
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n", encoding="utf-8")
        print("wrote", out_path.relative_to(ROOT))
    else:
        print(text)

    print(
        f"MILESTONE_READINESS score={report['score']} status={report['status']} gaps={len(report['gaps'])}",
        file=sys.stderr,
    )

    if args.strict and report["status"] != "achieved":
        return 1
    if report["status"] == "not_achieved":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
