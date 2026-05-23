#!/usr/bin/env python3
"""Validate organization registry consistency across schemas, workflows, and SSOT docs.

Run from repo root:
  python tools/validate_org_registry.py
Exit 0 if OK, 1 if mismatches found.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_PATHS = {
    "DispatchRequest": ROOT
    / "skills/platform/task-dispatcher/schemas/dispatch-request.v1.schema.json",
    "DeptWorkComplete": ROOT
    / "skills/development/product-manager/schemas/dept-work-complete.v1.schema.json",
    "Handoff v1.2 subtask": ROOT
    / "skills/planning/issue-story-planner/schemas/asana-buddy-handoff.v1.2.schema.json",
}

DOC_SNIPPET_CHECKS: list[tuple[str, Path]] = [
    ("dept-work-io.md", ROOT / "docs/design/dept-work-io.md"),
    ("handoff-v12-department.md", ROOT / "docs/design/handoff-v12-department.md"),
    ("task-dispatcher SKILL", ROOT / "skills/platform/task-dispatcher/SKILL.md"),
    ("issue-story-planner SKILL", ROOT / "skills/planning/issue-story-planner/SKILL.md"),
]


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
        elif in_deps and line.startswith("#") or (in_deps and line.startswith("coordination")):
            if current:
                deps.append(current)
            break
    if current and current not in deps:
        deps.append(current)
    return [d for d in deps if d.get("enabled", "true") != "false"]


def _schema_department_enum(schema_path: Path, pointer: str) -> set[str]:
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    if pointer == "dispatch":
        return set(data["properties"]["department"]["enum"])
    if pointer == "dept_complete":
        return set(data["properties"]["department"]["enum"])
    if pointer == "handoff_subtask":
        items = data["properties"]["subtasks"]["items"]["properties"]["department"]
        return set(items["enum"])
    raise ValueError(pointer)


def _check_file_exists(rel: str, dept_id: str) -> str | None:
    p = ROOT / rel
    if not p.is_file():
        return f"missing file: {rel} (department={dept_id})"
    return None


def main() -> int:
    errors: list[str] = []
    orgs = _load_orgs()
    dept_ids = sorted(d["id"] for d in orgs)
    print(f"organizations.yaml departments: {', '.join(dept_ids)}")

    enums = {
        "DispatchRequest": _schema_department_enum(SCHEMA_PATHS["DispatchRequest"], "dispatch"),
        "DeptWorkComplete": _schema_department_enum(SCHEMA_PATHS["DeptWorkComplete"], "dept_complete"),
        "Handoff v1.2": _schema_department_enum(SCHEMA_PATHS["Handoff v1.2 subtask"], "handoff_subtask"),
    }
    for name, enum in enums.items():
        missing = set(dept_ids) - enum
        extra = enum - set(dept_ids) - {"planning", "development", "analysis", "ux"}
        if missing:
            errors.append(f"{name} schema missing departments: {sorted(missing)}")
        if extra:
            errors.append(f"{name} schema has unknown departments: {sorted(extra)}")

    for dept in orgs:
        did = dept["id"]
        for key in ("workflow_id", "entry_agent", "delivery_io_doc", "skill_root", "output_root"):
            if key not in dept:
                errors.append(f"organizations.yaml department '{did}' missing '{key}'")
        wf = dept.get("workflow_id", "")
        errors.extend(
            filter(
                None,
                [
                    _check_file_exists(f"workflows/{wf}.yaml", did),
                    _check_file_exists(dept.get("delivery_io_doc", ""), did),
                    _check_file_exists(
                        f"skills/{did}/{dept.get('entry_agent', '')}/SKILL.md", did
                    )
                    if dept.get("entry_agent", "").endswith("-pm")
                    or (ROOT / f"skills/{did}").exists()
                    else None,
                ],
            )
        )
        pm = dept.get("entry_agent", "")
        pm_skill = ROOT / "skills" / did / pm / "SKILL.md"
        if not pm_skill.is_file():
            alt = list((ROOT / "skills" / did).glob(f"*/SKILL.md"))
            if not any(pm in str(p) for p in alt):
                errors.append(f"PM skill not found: skills/{did}/{pm}/SKILL.md")

    dept_io = (ROOT / "docs/design/dept-work-io.md").read_text(encoding="utf-8")
    for did in dept_ids:
        if did not in dept_io:
            errors.append(f"dept-work-io.md does not mention department '{did}'")

    team_conv = (ROOT / "docs/design/team-conventions.md").read_text(encoding="utf-8")
    for did in dept_ids:
        if f"`{did}`" not in team_conv:
            errors.append(f"team-conventions.md does not mention `{did}`")

    for label, path in DOC_SNIPPET_CHECKS:
        if not path.is_file():
            errors.append(f"{label}: file missing {path}")
            continue
        body = path.read_text(encoding="utf-8")
        for did in dept_ids:
            if did not in body:
                errors.append(f"{label}: {path.name} missing department '{did}'")

    examples_dir = ROOT / "skills/planning/issue-story-planner/examples"
    handoff_examples = list(examples_dir.glob("handoff*.json"))
    for did in dept_ids:
        if did == "planning":
            continue
        if not any(did in p.read_text(encoding="utf-8") for p in handoff_examples):
            errors.append(
                f"No handoff example JSON references department '{did}' "
                f"(add skills/planning/issue-story-planner/examples/handoff.*.json)"
            )

    if errors:
        print("\nVALIDATION FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("OK - organization registry is consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
