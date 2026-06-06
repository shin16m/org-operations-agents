"""Guards for agent-work-record comments and worker subtask completion."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parents[3]
_REGISTRY_PATH = _REPO_ROOT / "workflows/agent-registry.yaml"

AGENT_RECORD = "agent-work-record"

PM_SLUGS = frozenset(
    {
        "product-manager",
        "ux-pm",
        "analytics-pm",
        "governance-pm",
        "audit-pm",
        "planning-pm",
    }
)

PLATFORM_COMMENT_SLUGS = frozenset(
    {
        "workflow-orchestrator",
        "task-dispatcher",
        "asana-buddy",
    }
)


def _load_skill_paths() -> dict[str, str]:
    text = _REGISTRY_PATH.read_text(encoding="utf-8")
    agents: dict[str, str] = {}
    current: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- slug:"):
            current = stripped.split(":", 1)[1].strip()
            continue
        if not current or not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("skill_path:"):
            agents[current] = stripped.split(":", 1)[1].strip()
    return agents


def skill_md_for_slug(slug: str) -> str | None:
    skill_path = _load_skill_paths().get(slug)
    if not skill_path:
        return None
    md = _REPO_ROOT / skill_path / "SKILL.md"
    if not md.is_file():
        return None
    try:
        return md.resolve().relative_to(_REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return md.as_posix()


def has_agent_comment(task_gid: str, agent_slug: str, token: str) -> bool:
    from asana_program_common import list_task_comment_stories  # noqa: WPS433

    needle = f"agent: {agent_slug.strip()}"
    for story in list_task_comment_stories(task_gid, token):
        text = story.get("text") or ""
        if AGENT_RECORD in text and needle in text:
            return True
    return False


def _notes_assignee(task: dict[str, Any]) -> str | None:
    from asana_program_common import parse_task_assignment  # noqa: WPS433

    return parse_task_assignment(str(task.get("notes") or "")).get("assignee")


def _pm_child_gid(task: dict[str, Any]) -> str | None:
    parent = task.get("parent") or {}
    gid = parent.get("gid")
    return str(gid) if gid else None


def _requirements_writer_mode(notes: str, name: str) -> str | None:
    if re.search(r"mode\s*=\s*as-built-spec", notes, re.I) or "事後仕様" in name:
        return "spec"
    if re.search(r"mode\s*=\s*requirements", notes, re.I) or "要件" in name:
        return "requirements"
    return None


def _dev_review_kind(notes: str, name: str) -> str | None:
    m = re.search(r"review_kind:\s*(\w+)", notes, re.I)
    if m:
        return m.group(1).strip().lower()
    lower = (notes + name).lower()
    if "mismatch" in lower:
        return "mismatch"
    if "requirements" in lower or "要件" in notes:
        return "requirements"
    return None


def _attachment_names(task_gid: str, token: str) -> set[str]:
    from attach_task_files import list_attachments  # noqa: WPS433

    return {str(row.get("name") or "") for row in list_attachments(task_gid, token)}


def _has_md_suffix(names: set[str], suffix: str) -> bool:
    return any(name.endswith(suffix) for name in names if name)


def validate_comment_agent(
    *,
    task_gid: str,
    agent: str,
    skill: str,
    token: str,
) -> str | None:
    """Return error message or None if comment is allowed."""
    from asana_program_common import fetch_task, is_epic_task  # noqa: WPS433

    task = fetch_task(task_gid, token)
    assignee = _notes_assignee(task)
    agent = agent.strip()
    skill = skill.strip()

    if agent in PM_SLUGS:
        if assignee and assignee != agent:
            return (
                f"PM slug {agent!r} cannot comment on task assigned to {assignee!r}. "
                "PM は委譲集約・DeptWorkComplete のみ PM slug で comment する。"
            )
    elif agent in PLATFORM_COMMENT_SLUGS:
        if agent == "workflow-orchestrator" and is_epic_task(task_gid, token, task=task):
            pass
        elif assignee and assignee != agent:
            return (
                f"--agent {agent!r} must match notes 担当: {assignee!r} "
                f"(task {task_gid})"
            )
    elif assignee and assignee != agent:
        return (
            f"--agent {agent!r} must match notes 担当: {assignee!r} "
            f"(task {task_gid})"
        )

    expected_skill = skill_md_for_slug(agent)
    if expected_skill and skill.replace("\\", "/") != expected_skill:
        return (
            f"--skill must be {expected_skill!r} for agent {agent!r} "
            f"(got {skill!r})"
        )
    return None


def validate_worker_sub_complete(*, task_gid: str, token: str) -> str | None:
    """Return error message or None if worker sub may be completed."""
    from asana_program_common import fetch_task  # noqa: WPS433

    task = fetch_task(task_gid, token)
    assignee = _notes_assignee(task)
    if not assignee or assignee in PM_SLUGS:
        return None

    if not has_agent_comment(task_gid, assignee, token):
        return (
            f"complete blocked: no agent-work-record from {assignee!r} on task {task_gid}. "
            "ワーカーが comment_task してから complete する。"
        )

    notes = str(task.get("notes") or "")
    name = str(task.get("name") or "")
    names = _attachment_names(task_gid, token)

    if assignee == "requirements-writer":
        mode = _requirements_writer_mode(notes, name)
        pm_child = _pm_child_gid(task)
        if mode == "requirements" and pm_child:
            expected = f"{pm_child}-requirements.md"
            if expected not in names and not _has_md_suffix(names, "-requirements.md"):
                return (
                    f"complete blocked: attach {expected!r} to task {task_gid} "
                    "(requirements-writer · attach_task_files.py --also-gid <review_sub>)"
                )
        if mode == "spec" and pm_child:
            expected = f"{pm_child}-spec.md"
            if expected not in names and not _has_md_suffix(names, "-spec.md"):
                return (
                    f"complete blocked: attach {expected!r} to task {task_gid} "
                    "(requirements-writer as-built-spec)"
                )

    if assignee == "dev-reviewer":
        kind = _dev_review_kind(notes, name)
        if kind == "requirements" and not _has_md_suffix(names, "-requirements.md"):
            return (
                f"complete blocked: dev-reviewer requirements review needs "
                f"*-requirements.md attached on task {task_gid}"
            )
        if kind == "mismatch" and not _has_md_suffix(names, "-spec.md"):
            return (
                f"complete blocked: dev-reviewer mismatch review needs "
                f"*-spec.md attached on task {task_gid}"
            )

    return None
