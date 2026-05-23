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


def workflow_agents_from_yaml(wf_path: Path) -> set[str]:
    text = wf_path.read_text(encoding="utf-8")
    return set(re.findall(r"^\s+agent:\s+(\S+)\s*$", text, re.MULTILINE))


def assign_plan_slugs(plan_path: Path) -> set[str]:
    import json

    data = json.loads(plan_path.read_text(encoding="utf-8"))
    slugs: set[str] = set()
    for item in data.get("subtasks") or []:
        if assignee := item.get("assignee"):
            slugs.add(str(assignee))
    return slugs
