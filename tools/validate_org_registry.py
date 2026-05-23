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

if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from agent_registry_util import (  # noqa: E402
    CROSS_DEPT_WORKERS,
    assign_plan_slugs,
    enabled_skill_paths,
    load_agents,
    skill_md_for_slug,
    worker_team_slug,
    workflow_agents_from_yaml,
)

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


def _dispatch_ssot_section(body: str, dept_id: str) -> str:
    m = re.search(rf"^## {re.escape(dept_id)}\s*$", body, re.MULTILINE)
    if not m:
        return ""
    start = m.end()
    m2 = re.search(r"^## [a-z]", body[start:], re.MULTILINE)
    end = start + m2.start() if m2 else len(body)
    return body[start:end]


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

    dispatch_ssot = ROOT / "docs/design/dispatch-prompt-ssot.md"
    if not dispatch_ssot.is_file():
        errors.append("missing docs/design/dispatch-prompt-ssot.md")
    else:
        ssot_body = dispatch_ssot.read_text(encoding="utf-8")
        for did in dept_ids:
            if f"## {did}" not in ssot_body:
                errors.append(f"dispatch-prompt-ssot.md missing section ## {did}")
            if did in ("ux", "development", "analysis"):
                section = _dispatch_ssot_section(ssot_body, did)
                if "pm_assign_subtasks" not in section:
                    errors.append(f"dispatch-prompt-ssot.md #{did} missing pm_assign_subtasks")

    td_skill = (ROOT / "skills/platform/task-dispatcher/SKILL.md").read_text(encoding="utf-8")
    if "dispatch-prompt-ssot.md" not in td_skill:
        errors.append("task-dispatcher SKILL must reference dispatch-prompt-ssot.md")

    for wf_name in ("ux-delivery", "development-delivery", "analysis-delivery"):
        wf_path = ROOT / f"workflows/{wf_name}.yaml"
        if wf_path.is_file():
            wf_text = wf_path.read_text(encoding="utf-8")
            if "assignment_doc:" not in wf_text:
                errors.append(f"{wf_name}.yaml missing policy.assignment_doc")
            if "dispatch_prompt_ssot:" not in wf_text:
                errors.append(f"{wf_name}.yaml missing policy.dispatch_prompt_ssot")
            if "review_rework_ssot:" not in wf_text:
                errors.append(f"{wf_name}.yaml missing policy.review_rework_ssot")

    pm_skill = ROOT / "skills/development/product-manager/SKILL.md"
    if pm_skill.is_file():
        pm_text = pm_skill.read_text(encoding="utf-8")
        if "pm_assign_subtasks" not in pm_text or "output/development/app/" not in pm_text:
            errors.append("product-manager SKILL must forbid direct app/ writes and require pm_assign_subtasks")
        if "pm_emit_worker_prompt" not in pm_text or "pm-worker-dispatch-ssot" not in pm_text:
            errors.append("product-manager SKILL must reference L3b worker dispatch")
        if "pm-review-rework-ssot" not in pm_text:
            errors.append("product-manager SKILL must reference pm-review-rework-ssot")

    for pm_path in (
        ROOT / "skills/ux/ux-pm/SKILL.md",
        ROOT / "skills/analysis/analytics-pm/SKILL.md",
    ):
        if pm_path.is_file():
            pm_text = pm_path.read_text(encoding="utf-8")
            if "pm-review-rework-ssot" not in pm_text:
                errors.append(f"{pm_path.relative_to(ROOT)} must reference pm-review-rework-ssot")

    for assign_name in (
        "development-pm-assignment.md",
        "ux-pm-assignment.md",
        "analytics-pm-assignment.md",
    ):
        assign_path = ROOT / "docs/design" / assign_name
        if assign_path.is_file():
            assign_text = assign_path.read_text(encoding="utf-8")
            if "pm-review-rework-ssot" not in assign_text:
                errors.append(f"{assign_name} must reference pm-review-rework-ssot")
            if assign_name != "development-pm-assignment.md" and "pm-worker-dispatch-ssot" not in assign_text:
                if assign_name in ("ux-pm-assignment.md", "analytics-pm-assignment.md"):
                    errors.append(f"{assign_name} must reference pm-worker-dispatch-ssot")
            if "complete_task.py --undo" in assign_text and "使わない" not in assign_text:
                errors.append(f"{assign_name} must not document --undo for PM rework")

    worker_ssot = ROOT / "docs/design/pm-worker-dispatch-ssot.md"
    if not worker_ssot.is_file():
        errors.append("missing docs/design/pm-worker-dispatch-ssot.md")
    rework_ssot = ROOT / "docs/design/pm-review-rework-ssot.md"
    if not rework_ssot.is_file():
        errors.append("missing docs/design/pm-review-rework-ssot.md")
    emit_tool = ROOT / "tools/pm_emit_worker_prompt.py"
    if not emit_tool.is_file():
        errors.append("missing tools/pm_emit_worker_prompt.py")
    fix_tool = ROOT / "tools/pm_create_fix_subtask.py"
    if not fix_tool.is_file():
        errors.append("missing tools/pm_create_fix_subtask.py")
    rework_ssot_text = rework_ssot.read_text(encoding="utf-8") if rework_ssot.is_file() else ""
    if "pm_create_fix_subtask.py" not in rework_ssot_text:
        errors.append("pm-review-rework-ssot.md must document pm_create_fix_subtask.py")

    enabled_paths = enabled_skill_paths()
    agents_meta = load_agents()

    for wf_name in ("planning-delivery", "ux-delivery", "development-delivery", "analysis-delivery"):
        wf_path = ROOT / f"workflows/{wf_name}.yaml"
        if not wf_path.is_file():
            continue
        for agent in workflow_agents_from_yaml(wf_path):
            if agent == "asana-buddy":
                continue
            if agent not in agents_meta:
                errors.append(f"{wf_name}.yaml agent '{agent}' not in agent-registry.yaml")
                continue
            if not agents_meta[agent].get("enabled"):
                errors.append(f"{wf_name}.yaml agent '{agent}' is disabled in registry")
            try:
                skill_md_for_slug(agent)
            except (KeyError, FileNotFoundError) as exc:
                errors.append(f"{wf_name}.yaml agent '{agent}': {exc}")

    dev_wf = ROOT / "workflows/development-delivery.yaml"
    if dev_wf.is_file():
        for agent in workflow_agents_from_yaml(dev_wf):
            if agent in CROSS_DEPT_WORKERS:
                expected_team = CROSS_DEPT_WORKERS[agent]
                try:
                    team = worker_team_slug(agent)
                except (KeyError, ValueError) as exc:
                    errors.append(f"cross-dept worker {agent}: {exc}")
                    continue
                if team != expected_team:
                    errors.append(
                        f"cross-dept worker {agent}: expected skills/{expected_team}/, got team {team}"
                    )

    assign_globs: list[tuple[Path, str]] = [
        (ROOT / "skills/development/examples", "assign-plan*.json"),
        (ROOT / "skills/ux/examples", "assign-plan*.json"),
        (ROOT / "skills/analysis/examples", "assign-plan*.json"),
        (ROOT / "work/assign-plans", "*.json"),
    ]
    for base, pattern in assign_globs:
        if not base.is_dir():
            continue
        for plan_path in sorted(base.glob(pattern)):
            for slug in assign_plan_slugs(plan_path):
                if slug not in enabled_paths:
                    errors.append(f"{plan_path.relative_to(ROOT)}: unknown/disabled assignee '{slug}'")
                else:
                    try:
                        skill_md_for_slug(slug)
                    except FileNotFoundError as exc:
                        errors.append(f"{plan_path.relative_to(ROOT)} assignee '{slug}': {exc}")

    emit_snippet_path = ROOT / "tools/pm_emit_worker_prompt.py"
    if emit_snippet_path.is_file():
        emit_text = emit_snippet_path.read_text(encoding="utf-8")
        if "skill_md_for_slug" not in emit_text:
            errors.append("pm_emit_worker_prompt.py must resolve skill path via agent_registry_util")
        if "skills/{department}/{worker_slug}" in emit_text:
            errors.append("pm_emit_worker_prompt.py still hardcodes skills/{department}/{worker_slug}")

    registry_text = (ROOT / "workflows/agent-registry.yaml").read_text(encoding="utf-8")
    if "task-executor" in registry_text:
        errors.append("agent-registry.yaml must not register task-executor (removed)")
    if (ROOT / "workflows/with-execution.yaml").is_file():
        errors.append("workflows/with-execution.yaml must be removed with task-executor")
    if (ROOT / "skills/platform/task-executor").is_dir():
        errors.append("skills/platform/task-executor/ must be removed")
    if (ROOT / "skills/development/doc-writer").is_dir():
        errors.append("skills/development/doc-writer/ must be removed (use requirements-writer)")
    if (ROOT / "skills/development/reviewer").is_dir():
        errors.append("skills/development/reviewer/ must be removed (use dev-reviewer + qa-verifier)")
    for legacy_program in (ROOT / "skills/platform/asana-buddy/optional").glob("asana_*_program.py"):
        errors.append(f"{legacy_program.relative_to(ROOT)} must be removed (use handoff_to_asana.py)")
    if "doc-writer" in registry_text or re.search(r"slug:\s*reviewer\b", registry_text):
        errors.append("agent-registry.yaml must not register deprecated doc-writer / reviewer")

    if errors:
        print("\nVALIDATION FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("OK - organization registry is consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
