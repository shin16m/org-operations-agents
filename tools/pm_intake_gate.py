#!/usr/bin/env python3
"""Fail-fast gate before development PM intake (full-ui requires ## 依存).

Usage:
  python tools/pm_intake_gate.py --gid <DEVELOPMENT_CHILD_GID>
  python tools/pm_intake_gate.py --notes-file notes.md --profile full-ui
  python tools/pm_intake_gate.py --gid <GID> --plan skills/development/examples/assign-plan.full-ui-v1.json

Exit 0 when allowed; 1 when blocked.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
if str(ASANA_OPT) not in sys.path:
    sys.path.insert(0, str(ASANA_OPT))

DEPENDENCY_HEADINGS = ("## 依存（読み取り専用）", "## 依存")
PROFILE_RE = re.compile(r"^profile:\s*(\S+)\s*$", re.MULTILINE)


def parse_profile(notes: str, plan_profile: str | None = None) -> str | None:
    if plan_profile:
        return plan_profile.strip()
    match = PROFILE_RE.search(notes)
    return match.group(1) if match else None


def _dependency_section(notes: str) -> str:
    start = -1
    for heading in DEPENDENCY_HEADINGS:
        idx = notes.find(heading)
        if idx >= 0 and (start < 0 or idx < start):
            start = idx
    if start < 0:
        return ""
    body = notes[start:]
    next_heading = re.search(r"\n## (?!#)", body[len(DEPENDENCY_HEADINGS[0]) :])
    if next_heading:
        body = body[: len(DEPENDENCY_HEADINGS[0]) + next_heading.start()]
    return body


def check_full_ui_dependency(notes: str) -> list[str]:
    failures: list[str] = []
    if not any(h in notes for h in DEPENDENCY_HEADINGS):
        failures.append(
            "missing ## 依存（読み取り専用） in task notes "
            "(see docs/design/cross-team-artifact-bridge.md)"
        )
        return failures

    dep = _dependency_section(notes)
    if not re.search(r"output/(?:dryrun/)?ux/", dep, re.IGNORECASE):
        failures.append("## 依存 must reference output/ux/ artifact path")
    if not re.search(r"figma\.com", dep, re.IGNORECASE):
        failures.append("## 依存 must include Figma URL (figma.com)")

    if "profile: full-ui" in notes and "## 依存" in notes:
        if notes.index("## 依存") < notes.find("profile: full-ui"):
            failures.append("## 依存 must appear after profile: full-ui header block")

    return failures


def requires_full_ui_gate(notes: str, *, plan_profile: str | None = None) -> bool:
    profile = parse_profile(notes, plan_profile)
    return profile == "full-ui"


def check_development_intake(
    notes: str,
    *,
    plan_profile: str | None = None,
) -> tuple[bool, list[str]]:
    if not requires_full_ui_gate(notes, plan_profile=plan_profile):
        return True, []
    failures = check_full_ui_dependency(notes)
    return not failures, failures


def format_blocked(*, gid: str, tool: str, failures: list[str]) -> str:
    detail = "; ".join(failures)
    return f"BLOCKED  pm_intake_gate  gid={gid}  tool={tool}  reason={detail}"


def main() -> int:
    p = argparse.ArgumentParser(description="Development PM intake gate (full-ui ## 依存)")
    p.add_argument("--gid", help="Development child task GID (fetch notes from Asana)")
    p.add_argument("--notes-file", type=Path, help="Local notes markdown (offline check)")
    p.add_argument("--plan", type=Path, help="Assign plan JSON (reads profile field)")
    p.add_argument("--profile", help="Override delivery profile (e.g. full-ui)")
    args = p.parse_args()

    plan_profile = args.profile
    if args.plan and args.plan.is_file():
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        plan_profile = plan_profile or plan.get("profile")

    if args.notes_file:
        notes = args.notes_file.read_text(encoding="utf-8")
        gid = args.gid or "local"
    elif args.gid:
        from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: WPS433
        from asana_program_common import console_safe, fetch_task  # noqa: WPS433

        load_env_from_dotfile()
        task = fetch_task(args.gid, get_token())
        notes = str(task.get("notes") or "")
        gid = args.gid
        print(console_safe(f"Task: {task.get('name')} ({gid})"))
    else:
        print("Provide --gid or --notes-file", file=sys.stderr)
        return 2

    ok, failures = check_development_intake(notes, plan_profile=plan_profile)
    if ok:
        profile = parse_profile(notes, plan_profile) or "(not full-ui)"
        print(f"OK  pm_intake_gate  gid={gid}  profile={profile}")
        return 0

    from asana_program_common import console_safe  # noqa: WPS433

    print(console_safe(format_blocked(gid=gid, tool="pm_intake_gate.py", failures=failures)))
    for item in failures:
        print(console_safe(f"  - {item}"))
    print(
        console_safe(
            "HINT  Transfer UX DeptWorkComplete → notes ## 依存 "
            "(docs/design/development-pm-assignment.md § full-ui)"
        )
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
