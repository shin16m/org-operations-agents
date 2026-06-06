"""Load agent-registry.yaml and resolve skill paths by slug (not parent department)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "workflows/agent-registry.yaml"

# Workers owned by another department but referenced in a delivery workflow.
CROSS_DEPT_WORKERS: dict[str, str] = {
    "ux-reviewer": "ux",
}

# Meta skills that intentionally have no persona.md
PERSONA_EXEMPT_SLUGS: frozenset[str] = frozenset({"agent-creater"})

# L3 PM hubs — not subtask assignees in assign-plan examples
PM_HUB_SLUGS: frozenset[str] = frozenset(
    {
        "product-manager",
        "planning-pm",
        "ux-pm",
        "analytics-pm",
        "governance-pm",
        "audit-pm",
    }
)


def is_pm_hub_slug(slug: str) -> bool:
    return slug in PM_HUB_SLUGS or slug.endswith("-pm")


def load_agents(registry_path: Path | None = None) -> dict[str, dict[str, str | bool]]:
    path = registry_path or REGISTRY_PATH
    text = path.read_text(encoding="utf-8")
    agents: dict[str, dict[str, str | bool]] = {}
    current: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- slug:"):
            current = stripped.split(":", 1)[1].strip()
            agents[current] = {"enabled": True}
            continue
        if not current or not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("skill_path:"):
            agents[current]["skill_path"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("enabled:"):
            agents[current]["enabled"] = stripped.split(":", 1)[1].strip() == "true"
    return agents


def enabled_skill_paths(registry_path: Path | None = None) -> dict[str, str]:
    return {
        slug: str(meta["skill_path"])
        for slug, meta in load_agents(registry_path).items()
        if meta.get("enabled") and meta.get("skill_path")
    }


def skill_md_for_slug(slug: str, registry_path: Path | None = None) -> str:
    paths = enabled_skill_paths(registry_path)
    if slug not in paths:
        raise KeyError(f"Agent slug not in registry or disabled: {slug}")
    skill_path = paths[slug]
    md = ROOT / skill_path / "SKILL.md"
    if not md.is_file():
        raise FileNotFoundError(f"SKILL.md missing for {slug}: {md}")
    try:
        return md.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return md.as_posix()


def worker_team_slug(slug: str, registry_path: Path | None = None) -> str:
    """Infer team id from skill_path (skills/<team>/...)."""
    skill_path = enabled_skill_paths(registry_path)[slug]
    parts = Path(skill_path).parts
    if len(parts) >= 2 and parts[0] == "skills":
        return parts[1]
    raise ValueError(f"Cannot infer team from skill_path for {slug}: {skill_path}")


def _entry_agent_from_workflow(text: str) -> str | None:
    m = re.search(r"^\s+entry_agent:\s+(\S+)\s*$", text, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'")


def workflow_agents_from_yaml(wf_path: Path) -> set[str]:
    text = wf_path.read_text(encoding="utf-8")
    entry_agent = _entry_agent_from_workflow(text)
    agents: set[str] = set()
    for raw in re.findall(r"^\s+agent:\s+(\S+)\s*$", text, re.MULTILINE):
        agent = raw.strip().strip('"').strip("'")
        if agent == "{department}-pm" and entry_agent:
            agent = entry_agent
        agents.add(agent)
    return agents


def assign_plan_slugs(plan_path: Path) -> set[str]:
    import json

    data = json.loads(plan_path.read_text(encoding="utf-8"))
    slugs: set[str] = set()
    for item in data.get("subtasks") or []:
        if assignee := item.get("assignee"):
            slugs.add(str(assignee))
    return slugs


def persona_md_for_slug(slug: str, registry_path: Path | None = None) -> Path | None:
    """Return persona markdown path for slug, or None if missing / exempt."""
    if slug in PERSONA_EXEMPT_SLUGS:
        return None
    paths = enabled_skill_paths(registry_path)
    if slug not in paths:
        return None
    personas_dir = ROOT / paths[slug] / "personas"
    if not personas_dir.is_dir():
        return None
    canonical = personas_dir / f"{slug.replace('-', '_')}.md"
    if canonical.is_file():
        return canonical
    mds = sorted(personas_dir.glob("*.md"))
    return mds[0] if mds else None


def slugs_in_skill_persona_matrix(matrix_path: Path | None = None) -> set[str]:
    """Extract `slug` tokens from skill-persona-matrix.md table rows."""
    path = matrix_path or (ROOT / "docs/inventory/skill-persona-matrix.md")
    if not path.is_file():
        return set()
    return set(re.findall(r"\| `([^`]+)` \|", path.read_text(encoding="utf-8")))
