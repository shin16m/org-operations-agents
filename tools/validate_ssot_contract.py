#!/usr/bin/env python3
"""Validate SSOT cross-document contracts and forbidden stale patterns.

Run from repo root:
  python tools/validate_ssot_contract.py

Checks that key governance phrases appear across workflow-io-contract,
cursor rule, and orchestrator SKILL; flags known stale patterns.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_department_ids() -> list[str]:
    text = (ROOT / "workflows/organizations.yaml").read_text(encoding="utf-8")
    deps: list[str] = []
    in_deps = False
    for line in text.splitlines():
        if line.strip() == "departments:":
            in_deps = True
            continue
        if in_deps and line.startswith("  - id:"):
            deps.append(line.split(":", 1)[1].strip())
        elif in_deps and (line.startswith("#") or line.startswith("coordination")):
            break
    return deps


# All listed files must contain every substring (case-sensitive).
CROSS_FILE_CONTRACTS: list[dict] = [
    {
        "name": "post-gate execution separation",
        "files": [
            "docs/design/workflow-io-contract.md",
            ".cursor/rules/workflow-intake-required.mdc",
            "skills/platform/workflow-orchestrator/SKILL.md",
        ],
        "required_any": [
            ["asana_execute", "task-dispatcher"],
            ["pm_assign_subtasks", "L3b"],
        ],
        "required_all": [],
    },
    {
        "name": "worker comment agent slug",
        "files": [
            ".cursor/rules/workflow-intake-required.mdc",
            "skills/platform/workflow-orchestrator/SKILL.md",
            "docs/design/agent-asana-comment-signature.md",
        ],
        "required_any": [],
        "required_all": ["実作業ワーカーの slug"],
    },
    {
        "name": "epic completion summary",
        "files": [
            "skills/platform/workflow-orchestrator/SKILL.md",
            "docs/design/agent-asana-comment-signature.md",
        ],
        "required_any": [],
        "required_all": ["comment_epic_summary.py"],
    },
    {
        "name": "pm assign review gate",
        "files": [
            "docs/design/pm-assign-review-gate.md",
            "docs/design/workflow-io-contract.md",
            ".cursor/rules/workflow-intake-required.mdc",
        ],
        "required_any": [],
        "required_all": ["pm_review_gate"],
    },
    {
        "name": "all pm assignment review gate",
        "files": [
            "docs/design/development-pm-assignment.md",
            "docs/design/ux-pm-assignment.md",
            "docs/design/analytics-pm-assignment.md",
            "docs/design/governance-pm-assignment.md",
            "docs/design/audit-pm-assignment.md",
        ],
        "required_any": [],
        "required_all": ["create_pm_review_gate", "人間"],
    },
    {
        "name": "pm review gate dependencies",
        "files": [
            "docs/design/pm-assign-review-gate.md",
            "docs/design/planning-gate-vs-pm-review-gate.md",
        ],
        "required_any": [],
        "required_all": ["addDependencies"],
    },
    {
        "name": "task retro comment section",
        "files": [
            "docs/design/task-retrospective-ssot.md",
            "docs/design/agent-asana-comment-signature.md",
        ],
        "required_any": [],
        "required_all": ["レトロスペクティブ"],
    },
    {
        "name": "task retro epic aggregate",
        "files": [
            "docs/design/task-retrospective-ssot.md",
            "skills/platform/workflow-orchestrator/SKILL.md",
        ],
        "required_any": [],
        "required_all": ["aggregate_epic_retrospective"],
    },
    {
        "name": "audit team dispatch",
        "files": [
            "docs/design/workflow-io-contract.md",
            "docs/design/department-model.md",
            "docs/design/dispatch-prompt-ssot.md",
        ],
        "required_any": [],
        "required_all": ["audit"],
    },
    {
        "name": "comment readability v1.3 SSOT",
        "files": [
            "docs/design/agent-asana-comment-signature.md",
        ],
        "required_any": [],
        "required_all": ["build_human_comment_body", "4.4", "禁止表現"],
    },
    {
        "name": "comment readability dispatch refs",
        "files": [
            "docs/design/dispatch-prompt-ssot.md",
            "skills/platform/asana-buddy/SKILL.md",
        ],
        "required_any": [],
        "required_all": ["build_human_comment_body", "です・ます"],
    },
    {
        "name": "record-wait orchestrator checklist",
        "files": [
            "skills/platform/workflow-orchestrator/SKILL.md",
            "docs/design/asana-driven-ops.md",
        ],
        "required_any": [],
        "required_all": ["--record-wait", "§H"],
    },
]

FORBIDDEN_PATTERNS: list[tuple[str, str, str]] = [
    (
        "agent-registry development v2 note",
        "workflows/agent-registry.yaml",
        r"development-delivery v2",
    ),
    (
        "orchestrator gate v2 wording in comment SSOT",
        "docs/design/agent-asana-comment-signature.md",
        r"gate 判定",
    ),
]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    for contract in CROSS_FILE_CONTRACTS:
        name = contract["name"]
        for rel in contract["files"]:
            path = ROOT / rel
            if not path.is_file():
                errors.append(f"{name}: missing file {rel}")
                continue
            body = _read(rel)
            for term in contract.get("required_all", []):
                if term not in body:
                    errors.append(f"{name}: {rel} missing required {term!r}")
            groups = contract.get("required_any") or []
            for group in groups:
                if not any(t in body for t in group):
                    errors.append(
                        f"{name}: {rel} missing any of {group!r}"
                    )

    for label, rel, pattern in FORBIDDEN_PATTERNS:
        path = ROOT / rel
        if not path.is_file():
            continue
        if re.search(pattern, _read(rel)):
            errors.append(f"forbidden pattern ({label}): {rel} matches {pattern!r}")

    dept_ids = _load_department_ids()
    team_conv = ROOT / "docs/design/team-conventions.md"
    dept_io = ROOT / "docs/design/dept-work-io.md"
    for doc_path, label in ((team_conv, "team-conventions"), (dept_io, "dept-work-io")):
        if not doc_path.is_file():
            errors.append(f"{label}: missing {doc_path.relative_to(ROOT)}")
            continue
        body = _read(str(doc_path.relative_to(ROOT)))
        for did in dept_ids:
            if f"`{did}`" not in body:
                errors.append(f"{label}: missing department `{did}`")

    cursor_rule = ROOT / ".cursor/rules/workflow-intake-required.mdc"
    if cursor_rule.is_file():
        body = _read(str(cursor_rule.relative_to(ROOT)))
        if "audit" not in body:
            errors.append("workflow-intake-required.mdc missing audit department reference")

    if errors:
        print("\nSSOT CONTRACT VALIDATION FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("OK - SSOT cross-document contracts satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
