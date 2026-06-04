#!/usr/bin/env python3
"""Load dispatch prompt snippets from dispatch-prompt-ssot.md."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISPATCH_SSOT = ROOT / "docs/design/dispatch-prompt-ssot.md"

EXECUTION_DISPATCH_ORDER = ("ux", "development", "analysis", "governance", "audit")

TITLE_DEPT_HINTS: tuple[tuple[str, str], ...] = (
    ("UX", "ux"),
    ("開発", "development"),
    ("分析", "analysis"),
    ("組織改善", "governance"),
    ("監査", "audit"),
    ("企画", "planning"),
)


def load_organizations() -> dict:
    path = ROOT / "workflows/organizations.yaml"
    text = path.read_text(encoding="utf-8")
    deps: dict[str, dict] = {}
    pillar_defaults: list = []
    section = None
    current: dict | None = None
    pillar_rule: dict | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "departments:":
            section = "departments"
            continue
        if stripped == "pillar_defaults:":
            section = "pillar_defaults"
            continue
        if stripped.startswith("coordination_group:"):
            section = "coordination"
            continue

        if section == "departments" and line.startswith("  - id:"):
            if current and current.get("enabled", "true") != "false":
                deps[current["id"]] = current
            current = {"id": line.split(":", 1)[1].strip()}
        elif section == "departments" and line.startswith("    ") and ":" in line and current:
            key, val = line.strip().split(":", 1)
            current[key] = val.strip()
        elif section == "pillar_defaults" and line.startswith("  - match:"):
            if pillar_rule:
                pillar_defaults.append(pillar_rule)
            pillar_rule = {"match": [], "department": None}
        elif section == "pillar_defaults" and pillar_rule is not None:
            if line.strip().startswith("department:"):
                pillar_rule["department"] = line.split(":", 1)[1].strip()
            elif line.strip().startswith("- "):
                pillar_rule["match"].append(line.strip()[2:].strip().strip('"'))
        elif section == "coordination" and line.startswith("  - id:"):
            break

    if current and current.get("enabled", "true") != "false":
        deps[current["id"]] = current
    if pillar_rule:
        pillar_defaults.append(pillar_rule)

    return {"departments": deps, "pillar_defaults": pillar_defaults}


def infer_department(*, notes: str, title: str, pillar_defaults: list | None = None) -> str | None:
    m = re.search(r"チーム:\s*(\S+)", notes or "")
    if m:
        return m.group(1).strip().lower()
    m = re.search(r"department:\s*(\S+)", notes or "", re.I)
    if m:
        return m.group(1).strip().lower()
    for hint, dept in TITLE_DEPT_HINTS:
        if hint in (title or ""):
            return dept
    text = f"{title}\n{notes}"
    for rule in pillar_defaults or []:
        dept = rule.get("department")
        for kw in rule.get("match") or []:
            if kw and kw in text:
                return str(dept)
    return None


def load_dispatch_prompt(department: str) -> str:
    text = DISPATCH_SSOT.read_text(encoding="utf-8")
    pattern = rf"(?ms)^##\s+{re.escape(department)}\s*\n.*?\n```\n(.*?)\n```"
    m = re.search(pattern, text)
    if not m:
        raise KeyError(f"dispatch prompt section not found: {department}")
    return m.group(1).strip()


def render_dispatch_prompt(*, department: str, task_gid: str, parent_gid: str) -> str:
    template = load_dispatch_prompt(department)
    return template.replace("{task_gid}", task_gid).replace("{parent_gid}", parent_gid)


def resolve_entry_agent(department: str, org: dict | None = None) -> str:
    org = org or load_organizations()
    dept = org["departments"].get(department)
    if not dept:
        raise KeyError(f"unknown department: {department}")
    return str(dept["entry_agent"])
