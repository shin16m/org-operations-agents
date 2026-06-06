#!/usr/bin/env python3
"""Validate a newly added skill slug is wired (registry · persona · matrix · workflow).

Usage:
  python tools/check_new_skill.py --slug design-system-owner
  python tools/check_new_skill.py --slug design-system-owner --department ux
  python tools/check_new_skill.py --all-enabled

Exit 0 if all checks pass; 1 otherwise.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from agent_registry_util import (  # noqa: E402
    PERSONA_EXEMPT_SLUGS,
    enabled_skill_paths,
    is_pm_hub_slug,
    load_agents,
    persona_md_for_slug,
    skill_md_for_slug,
    slugs_in_skill_persona_matrix,
    workflow_agents_from_yaml,
    worker_team_slug,
)


def _check_slug(slug: str, department: str | None) -> list[str]:
    failures: list[str] = []
    agents = load_agents()
    if slug not in agents:
        failures.append(f"registry: slug '{slug}' not in agent-registry.yaml")
        return failures
    if not agents[slug].get("enabled"):
        failures.append(f"registry: slug '{slug}' is disabled")

    try:
        skill_md_for_slug(slug)
    except (KeyError, FileNotFoundError) as exc:
        failures.append(f"SKILL.md: {exc}")

    if slug not in PERSONA_EXEMPT_SLUGS:
        persona = persona_md_for_slug(slug)
        if not persona:
            failures.append(
                f"persona: missing personas/{slug.replace('-', '_')}.md "
                f"(see docs/design/skill-persona-principles.md)"
            )
        else:
            body = persona.read_text(encoding="utf-8")
            if "**志向:**" not in body and "志向:" not in body:
                failures.append(f"persona: {persona.relative_to(ROOT)} missing 志向 line")

    matrix = slugs_in_skill_persona_matrix()
    if slug not in matrix:
        failures.append(
            f"matrix: docs/inventory/skill-persona-matrix.md missing row for `{slug}`"
        )

    display = ROOT / "workflows/agent-display-names.yaml"
    if display.is_file() and f"{slug}:" not in display.read_text(encoding="utf-8"):
        failures.append(f"display-names: workflows/agent-display-names.yaml missing '{slug}'")

    inv = ROOT / "docs/inventory/skills-inventory.md"
    if inv.is_file() and slug not in inv.read_text(encoding="utf-8"):
        failures.append(f"inventory: docs/inventory/skills-inventory.md missing '{slug}'")

    dept = department or _infer_department(slug)
    if dept:
        wf = ROOT / f"workflows/{dept}-delivery.yaml"
        if wf.is_file():
            wf_agents = workflow_agents_from_yaml(wf)
            if slug not in wf_agents and not is_pm_hub_slug(slug):
                failures.append(
                    f"workflow: workflows/{dept}-delivery.yaml does not list agent '{slug}'"
                )
        examples = ROOT / f"skills/{dept}/examples"
        if examples.is_dir() and not is_pm_hub_slug(slug):
            plans = list(examples.glob("assign-plan*.json"))
            if plans:
                found = any(
                    f'"assignee": "{slug}"' in p.read_text(encoding="utf-8") for p in plans
                )
                if not found:
                    failures.append(
                        f"assign-plan: no skills/{dept}/examples/assign-plan*.json "
                        f"references assignee '{slug}'"
                    )

    return failures


def _infer_department(slug: str) -> str | None:
    try:
        team = worker_team_slug(slug)
    except (KeyError, ValueError):
        return None
    if team == "platform":
        return None
    return team


def main() -> int:
    p = argparse.ArgumentParser(description="Check new skill wiring")
    p.add_argument("--slug", help="Agent slug to validate")
    p.add_argument("--department", help="Department id (ux, analysis, ...)")
    p.add_argument("--all-enabled", action="store_true", help="Validate every enabled slug")
    args = p.parse_args()

    if args.all_enabled:
        slugs = sorted(enabled_skill_paths().keys())
    elif args.slug:
        slugs = [args.slug]
    else:
        p.error("specify --slug <id> or --all-enabled")

    total: list[tuple[str, str]] = []
    for slug in slugs:
        fails = _check_slug(slug, args.department if not args.all_enabled else None)
        if fails:
            print(f"\n[{slug}] {len(fails)} FAIL")
            for f in fails:
                print(f"  - {f}")
                total.append((slug, f))
        else:
            print(f"[{slug}] OK")

    if total:
        print(f"\nFAILED: {len(total)} check(s)", file=sys.stderr)
        return 1
    print(f"\nOK - {len(slugs)} slug(s) pass check_new_skill.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
