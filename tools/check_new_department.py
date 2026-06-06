#!/usr/bin/env python3
"""Mechanical coverage check for new-department-checklist.md (A-E required rows).

Usage:
  python tools/check_new_department.py --department audit
  python tools/check_new_department.py --department planning
  python tools/check_new_department.py --all

Exit 0 if all required checks pass for the target department(s); 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))


def _load_orgs() -> list[dict[str, str]]:
    text = (ROOT / "workflows/organizations.yaml").read_text(encoding="utf-8")
    deps: list[dict[str, str]] = []
    in_deps = False
    current: dict[str, str] = {}
    for line in text.splitlines():
        if line.strip() == "departments:":
            in_deps = True
            continue
        if in_deps and line.startswith("  - id:"):
            if current:
                deps.append(current)
            current = {"id": line.split(":", 1)[1].strip()}
        elif in_deps and line.startswith("    ") and ":" in line and current:
            key, val = line.strip().split(":", 1)
            current[key] = val.strip()
        elif in_deps and (line.startswith("#") or line.startswith("coordination")):
            if current:
                deps.append(current)
            break
    if current and current not in deps:
        deps.append(current)
    return [d for d in deps if d.get("enabled", "true") != "false"]


SCHEMA_FILES: dict[str, Path] = {
    "B1 dispatch-request": ROOT
    / "skills/platform/task-dispatcher/schemas/dispatch-request.v1.schema.json",
    "B2 dept-work-complete": ROOT
    / "skills/development/product-manager/schemas/dept-work-complete.v1.schema.json",
    "B3 asana-buddy-handoff v1.2": ROOT
    / "skills/planning/issue-story-planner/schemas/asana-buddy-handoff.v1.2.schema.json",
}

DOC_MENTION_CHECKS: dict[str, Path] = {
    "C1 dept-work-io": ROOT / "docs/design/dept-work-io.md",
    "C2 handoff-v12-department": ROOT / "docs/design/handoff-v12-department.md",
    "C4 department-model": ROOT / "docs/design/department-model.md",
    "C5 task-dispatcher SKILL": ROOT / "skills/platform/task-dispatcher/SKILL.md",
    "C7 issue-story-planner SKILL": ROOT / "skills/planning/issue-story-planner/SKILL.md",
    "C12 dispatch-prompt-ssot": ROOT / "docs/design/dispatch-prompt-ssot.md",
}


def _schema_enum(schema_path: Path) -> set[str]:
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    props = data.get("properties", {})
    if "department" in props:
        return set(props["department"].get("enum") or [])
    subs = props.get("subtasks", {}).get("items", {}).get("properties", {})
    if "department" in subs:
        return set(subs["department"].get("enum") or [])
    return set()


def _has_dryrun_artifact(did: str) -> bool:
    ver_dir = ROOT / "docs/verification"
    if ver_dir.is_dir():
        for path in ver_dir.glob("*dryrun*.md"):
            if did in path.read_text(encoding="utf-8"):
                return True
    tools_dir = ROOT / "tools"
    if tools_dir.is_dir():
        for path in tools_dir.glob("run_*dryrun*.py"):
            if f'"{did}"' in path.read_text(encoding="utf-8"):
                return True
    return False


def _entry_agent(orgs: list[dict[str, str]], did: str) -> str:
    for d in orgs:
        if d["id"] == did:
            return d.get("entry_agent", "")
    return ""


def _check_dept(did: str, orgs: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    entry = _entry_agent(orgs, did)

    # A1
    org_text = (ROOT / "workflows/organizations.yaml").read_text(encoding="utf-8")
    if f"- id: {did}" not in org_text:
        failures.append(f"A1 organizations.yaml: '- id: {did}' not found")

    # A2
    wf = ROOT / f"workflows/{did}-delivery.yaml"
    if not wf.is_file():
        failures.append(f"A2 missing workflow: workflows/{did}-delivery.yaml")
    else:
        wf_text = wf.read_text(encoding="utf-8")
        if "entry_agent:" not in wf_text:
            failures.append(f"A2 {wf.name}: missing entry_agent:")

    # A3
    io_doc = ROOT / f"docs/design/{did}-delivery-io.md"
    if not io_doc.is_file():
        failures.append(f"A3 missing: docs/design/{did}-delivery-io.md")

    # A4
    if entry:
        pm_skill = ROOT / f"skills/{did}/{entry}/SKILL.md"
        if not pm_skill.is_file():
            failures.append(f"A4 missing PM SKILL: skills/{did}/{entry}/SKILL.md")

    # A5
    registry_text = (ROOT / "workflows/agent-registry.yaml").read_text(encoding="utf-8")
    if entry and not re.search(rf"-\s+slug:\s+{re.escape(entry)}\b", registry_text):
        failures.append(f"A5 agent-registry.yaml: PM slug '{entry}' not registered")

    # B1-B3
    for label, schema_path in SCHEMA_FILES.items():
        if not schema_path.is_file():
            failures.append(f"{label}: schema missing")
            continue
        enum = _schema_enum(schema_path)
        if did not in enum:
            failures.append(f"{label}: department enum missing '{did}' (have: {sorted(enum)})")

    # C1, C2, C4, C5, C7
    for label, path in DOC_MENTION_CHECKS.items():
        if not path.is_file():
            failures.append(f"{label}: file missing {path.relative_to(ROOT)}")
            continue
        body = path.read_text(encoding="utf-8")
        if did not in body:
            failures.append(f"{label}: missing department '{did}'")

    # C3 team-conventions — require backticked id
    team_conv = ROOT / "docs/design/team-conventions.md"
    if team_conv.is_file():
        if f"`{did}`" not in team_conv.read_text(encoding="utf-8"):
            failures.append(f"C3 team-conventions.md: missing `{did}`")

    # C9 skills-inventory PM mention
    inv = ROOT / "docs/inventory/skills-inventory.md"
    if inv.is_file() and entry and entry not in inv.read_text(encoding="utf-8"):
        failures.append(f"C9 skills-inventory.md: missing PM slug '{entry}'")

    # C11 root README
    readme = ROOT / "README.md"
    if readme.is_file():
        body = readme.read_text(encoding="utf-8")
        if did not in body and (entry and entry not in body):
            failures.append(f"C11 README.md: missing department '{did}' and PM '{entry}'")

    # C12 dispatch-prompt-ssot must have '## <id>' section
    dispatch_ssot = ROOT / "docs/design/dispatch-prompt-ssot.md"
    if dispatch_ssot.is_file():
        if not re.search(rf"^## {re.escape(did)}\s*$", dispatch_ssot.read_text(encoding="utf-8"), re.MULTILINE):
            failures.append(f"C12 dispatch-prompt-ssot.md: missing '## {did}' section")

    # D1 PM strict-ops assignment doc (optional for planning)
    if did != "planning":
        assign_map = {
            "ux": "ux-pm-assignment.md",
            "development": "development-pm-assignment.md",
            "analysis": "analytics-pm-assignment.md",
            "audit": "audit-pm-assignment.md",
            "governance": "governance-pm-assignment.md",
        }
        fname = assign_map.get(did, f"{did}-pm-assignment.md")
        assign_path = ROOT / f"docs/design/{fname}"
        if not assign_path.is_file():
            failures.append(f"D1 missing: docs/design/{fname}")
        else:
            assign_body = assign_path.read_text(encoding="utf-8")
            for token in ("human_review_gate", "opt-in", "pm-review-rework-ssot"):
                if token not in assign_body:
                    failures.append(f"D1 {fname}: missing '{token}'")
            if "pm_assign_subtasks" not in assign_body:
                failures.append(f"D1 {fname}: missing pm_assign_subtasks")

        # D4 assign plan examples
        examples = ROOT / f"skills/{did}/examples"
        if not examples.is_dir() or not list(examples.glob("assign-plan*.json")):
            failures.append(
                f"D4 missing: skills/{did}/examples/assign-plan*.json "
                "(add at least one assign plan example)"
            )

        # D6 dryrun doc or script referencing department
        if not _has_dryrun_artifact(did):
            failures.append(
                f"D6 missing dryrun: docs/verification/*dryrun*.md or tools/run_*dryrun*.py "
                f"must mention department '{did}'"
            )

        # I1 delivery-strength / team-conventions cross-link
        dsp = ROOT / "docs/design/delivery-strength-pattern.md"
        if dsp.is_file() and f"`{did}`" not in dsp.read_text(encoding="utf-8"):
            if did in ("ux", "development", "analysis"):
                failures.append(
                    f"I1 delivery-strength-pattern.md: missing `{did}` in application matrix"
                )

        # J1 skill-persona-matrix lists department PM
        if entry:
            matrix = ROOT / "docs/inventory/skill-persona-matrix.md"
            if matrix.is_file() and f"`{entry}`" not in matrix.read_text(encoding="utf-8"):
                failures.append(
                    f"J1 skill-persona-matrix.md: missing PM slug `{entry}`"
                )

    # E1 handoff example referencing department
    examples_dir = ROOT / "skills/planning/issue-story-planner/examples"
    if examples_dir.is_dir() and did != "planning":
        ok = any(
            f'"department": "{did}"' in p.read_text(encoding="utf-8")
            for p in examples_dir.glob("handoff*.json")
        )
        if not ok:
            failures.append(
                f"E1 no handoff example references department '{did}' in skills/planning/issue-story-planner/examples/"
            )

    return failures


def main() -> int:
    p = argparse.ArgumentParser(description="Check new-department-checklist coverage")
    p.add_argument("--department", help="Department id to check (e.g. audit)")
    p.add_argument("--all", action="store_true", help="Check all enabled departments")
    args = p.parse_args()

    if not args.department and not args.all:
        p.error("specify --department <id> or --all")

    orgs = _load_orgs()
    enabled_ids = [d["id"] for d in orgs]

    targets = enabled_ids if args.all else [args.department]
    for t in targets:
        if t not in enabled_ids:
            print(
                f"ERROR: department '{t}' not in enabled organizations.yaml ({enabled_ids})",
                file=sys.stderr,
            )
            return 2

    total_failures: list[tuple[str, str]] = []
    for did in targets:
        fails = _check_dept(did, orgs)
        if fails:
            print(f"\n[{did}] {len(fails)} FAIL")
            for f in fails:
                print(f"  - {f}")
                total_failures.append((did, f))
        else:
            print(f"[{did}] OK")

    if total_failures:
        print(
            f"\nFAILED: {len(total_failures)} check(s) across {len(set(d for d, _ in total_failures))} department(s)",
            file=sys.stderr,
        )
        return 1
    print(f"\nOK - {len(targets)} department(s) pass new-department-checklist coverage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
