"""Shared helpers for asana-buddy batch programs and handoff JSON import."""
from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

_REPO_ROOT = Path(__file__).resolve().parents[4]


def console_safe(text: str) -> str:
    """Encode for the current stdout (e.g. cp932 on Windows) without raising."""
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        return text.encode(enc, errors="replace").decode(enc, errors="replace")
    except LookupError:
        return text.encode("utf-8", errors="replace").decode("utf-8")

import requests

from agent_handler_asana import ASANA_BASE, create_task

FALLBACK_PROJECT_GID = "1214771428861230"

# 担当種別 enum CF（プロジェクト 1214771428861230 · override via .env）
DEFAULT_ASSIGNEE_TYPE_FIELD_GID = "1215082835199209"
DEFAULT_ASSIGNEE_TYPE_AI_GID = "1215082835199211"
DEFAULT_ASSIGNEE_TYPE_HUMAN_GID = "1215082835199210"

TASK_OPT_FIELDS = "name,notes,completed,permalink_url,parent.gid,parent.name"


def fetch_task(task_gid: str, token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{ASANA_BASE}/tasks/{task_gid}",
        headers=headers,
        params={"opt_fields": TASK_OPT_FIELDS},
    )
    r.raise_for_status()
    return r.json()["data"]


def assignee_type_config() -> dict[str, str] | None:
    """Return field + enum option GIDs for 担当種別, or None if disabled."""
    if os.getenv("ASANA_ASSIGNEE_TYPE_DISABLED", "").strip().lower() in ("1", "true", "yes"):
        return None
    field = (
        os.getenv("ASANA_ASSIGNEE_TYPE_FIELD_GID", "").strip()
        or DEFAULT_ASSIGNEE_TYPE_FIELD_GID
    )
    ai = (
        os.getenv("ASANA_ASSIGNEE_TYPE_AI_GID", "").strip()
        or DEFAULT_ASSIGNEE_TYPE_AI_GID
    )
    human = (
        os.getenv("ASANA_ASSIGNEE_TYPE_HUMAN_GID", "").strip()
        or DEFAULT_ASSIGNEE_TYPE_HUMAN_GID
    )
    if not field:
        return None
    return {"field_gid": field, "ai_gid": ai, "human_gid": human}


def set_assignee_type(task_gid: str, kind: str, token: str) -> bool:
    """Set 担当種別 custom field to AI or human. Returns True if set."""
    cfg = assignee_type_config()
    if not cfg:
        return False
    kind_norm = kind.strip()
    if kind_norm not in ("AI", "human"):
        raise ValueError(f"assignee type must be 'AI' or 'human', got {kind!r}")
    opt_gid = cfg["ai_gid"] if kind_norm == "AI" else cfg["human_gid"]
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.put(
        f"{ASANA_BASE}/tasks/{task_gid}",
        json={"data": {"custom_fields": {cfg["field_gid"]: opt_gid}}},
        headers=headers,
    )
    r.raise_for_status()
    return True


def set_assignee_type_org_ops(task_gid: str, token: str) -> bool:
    """org-ops CLI が作成/更新するタスク → 担当種別 AI。"""
    try:
        return set_assignee_type(task_gid, "AI", token)
    except requests.HTTPError as exc:
        print(
            f"警告: 担当種別 CF を設定できませんでした task={task_gid}: {exc}",
            file=sys.stderr,
        )
        return False


def add_task_to_project(task_gid: str, project_gid: str, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        f"{ASANA_BASE}/tasks/{task_gid}/addProject",
        json={"data": {"project": project_gid}},
        headers=headers,
    )
    r.raise_for_status()


def task_project_gid(task_gid: str, token: str) -> str | None:
    """Return first project GID on task (for subtask CF inheritance)."""
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{ASANA_BASE}/tasks/{task_gid}",
        headers=headers,
        params={"opt_fields": "projects.gid,memberships.project.gid"},
    )
    r.raise_for_status()
    data = r.json()["data"]
    projects = data.get("projects") or []
    if projects:
        return projects[0].get("gid")
    for m in data.get("memberships") or []:
        proj = (m.get("project") or {}).get("gid")
        if proj:
            return proj
    return None


def ensure_subtask_project_membership(sub_gid: str, parent_gid: str, token: str) -> None:
    """Subtasks need project membership before project-scoped custom fields apply."""
    project = task_project_gid(parent_gid, token) or resolve_project_with_fallback(None)
    if not project:
        return
    try:
        add_task_to_project(sub_gid, project, token)
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 400:
            return
        raise


_DISPLAY_NAMES_CACHE: dict[str, str] | None = None


def load_agent_display_names() -> dict[str, str]:
    """Load slug → 依頼者向け表示名 from workflows/agent-display-names.yaml."""
    global _DISPLAY_NAMES_CACHE
    if _DISPLAY_NAMES_CACHE is not None:
        return _DISPLAY_NAMES_CACHE
    path = _REPO_ROOT / "workflows/agent-display-names.yaml"
    names: dict[str, str] = {}
    if path.is_file():
        in_block = False
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped == "display_names:":
                in_block = True
                continue
            if not in_block or not stripped or stripped.startswith("#"):
                continue
            if ":" in stripped:
                key, _, val = stripped.partition(":")
                names[key.strip()] = val.strip()
    _DISPLAY_NAMES_CACHE = names
    return names


def agent_display_name(slug: str) -> str:
    return load_agent_display_names().get(slug.strip(), slug.strip())


def _signature_block(
    agent: str,
    skill_path: str,
    *,
    phase: str = "complete",
    executed_at: str | None = None,
    model: str | None = None,
) -> str:
    ts = executed_at or datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    lines = [
        "---",
        "🤖 agent-work-record",
        f"agent: {agent.strip()}",
        f"skill: {skill_path.strip()}",
        f"phase: {phase.strip() or 'complete'}",
        f"executed_at: {ts}",
    ]
    if model and model.strip():
        lines.append(f"model: {model.strip()}")
    lines.append("---")
    return "\n".join(lines)


def format_signed_comment(
    agent: str,
    skill_path: str,
    body: str,
    *,
    phase: str = "complete",
    executed_at: str | None = None,
    model: str | None = None,
    summary: str | None = None,
    artifacts: Sequence[str] | None = None,
) -> str:
    """Build Asana story: v1.2 — human block first, agent-work-record signature last."""
    display = agent_display_name(agent)
    human_lines = ["## 依頼者向け", "", f"**担当:** {display}"]
    if summary and summary.strip():
        human_lines.append(f"**要約:** {summary.strip()}")
    human_lines.append("")
    main = (body or "").strip()
    if main:
        human_lines.append(main)
    elif not (summary and summary.strip()):
        human_lines.append("作業が完了しました。")
    if artifacts:
        artifact_lines = "\n".join(f"- {a}" for a in artifacts if a and str(a).strip())
        if artifact_lines:
            human_lines.extend(["", "## 成果物", artifact_lines])
    human_block = "\n".join(human_lines).strip()
    sig = _signature_block(
        agent, skill_path, phase=phase, executed_at=executed_at, model=model
    )
    return f"{human_block}\n\n---\n\n{sig}\n"


def create_task_story(task_gid: str, text: str, token: str) -> dict[str, Any]:
    """Post a comment (story) on an Asana task."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"data": {"text": text}}
    r = requests.post(
        f"{ASANA_BASE}/tasks/{task_gid}/stories",
        json=payload,
        headers=headers,
    )
    r.raise_for_status()
    return r.json()["data"]


def load_agent_work_comment(path: str) -> dict[str, Any]:
    import json
    from pathlib import Path

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0":
        raise ValueError('agent work comment schema_version must be "1.0"')
    for key in ("task_gid", "agent", "skill_path", "summary"):
        if not (data.get(key) or "").strip():
            raise ValueError(f"agent work comment {key} is required")
    return data


def agent_work_comment_to_text(data: dict[str, Any]) -> str:
    body = (data.get("body_markdown") or "").strip()
    if not body:
        body = data["summary"].strip()
    return format_signed_comment(
        data["agent"],
        data["skill_path"],
        body,
        phase=data.get("phase") or "complete",
        executed_at=data.get("executed_at"),
        model=data.get("model"),
        summary=data.get("summary"),
        artifacts=data.get("artifacts"),
    )


def set_task_completed(task_gid: str, completed: bool, token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.put(
        f"{ASANA_BASE}/tasks/{task_gid}",
        json={"data": {"completed": completed}},
        headers=headers,
    )
    r.raise_for_status()
    return r.json()["data"]


def list_subtasks(parent_gid: str, token: str) -> list[dict[str, Any]]:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{ASANA_BASE}/tasks/{parent_gid}/subtasks",
        headers=headers,
        params={"opt_fields": "name,completed,gid,notes"},
    )
    r.raise_for_status()
    return r.json()["data"]


ASSIGNEE_LINE = re.compile(r"^担当:\s*(\S+)\s*$", re.MULTILINE)
STATUS_LINE = re.compile(r"^状態:\s*(\S+)\s*$", re.MULTILINE)
# Write `チーム:`; parse accepts legacy `課:` for backward compatibility.
DEPT_LINE_WRITE = "チーム"
DEPT_LINE_PARSE = re.compile(r"^(?:課|チーム):\s*(\S+)\s*$", re.MULTILINE)
DEPT_LINE_STRIP = re.compile(r"^(?:課|チーム):\s*\S+\s*$", re.MULTILINE)


def parse_task_assignment(notes: str) -> dict[str, str | None]:
    """Parse チーム / 担当 / 状態 from task notes header."""
    return {
        "department": (m.group(1) if (m := DEPT_LINE_PARSE.search(notes or "")) else None),
        "assignee": (m.group(1) if (m := ASSIGNEE_LINE.search(notes or "")) else None),
        "status": (m.group(1) if (m := STATUS_LINE.search(notes or "")) else None),
    }


def format_assignment_header(
    *,
    department: str | None = None,
    assignee: str | None = None,
    status: str | None = None,
) -> str:
    lines: list[str] = []
    if department:
        lines.append(f"{DEPT_LINE_WRITE}: {department.strip()}")
    if assignee:
        lines.append(f"担当: {assignee.strip()}")
    if status:
        lines.append(f"状態: {status.strip()}")
    return "\n".join(lines) + ("\n\n" if lines else "")


def merge_notes_with_assignment(
    existing_notes: str,
    *,
    department: str | None = None,
    assignee: str | None = None,
    status: str | None = None,
) -> str:
    """Replace or prepend assignment header; keep ## 背景以下."""
    body = existing_notes or ""
    for pat in (DEPT_LINE_STRIP, ASSIGNEE_LINE, STATUS_LINE):
        body = pat.sub("", body)
    body = body.strip()
    header = format_assignment_header(department=department, assignee=assignee, status=status)
    return (header + body).strip()


def update_task_notes(task_gid: str, notes: str, token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.put(
        f"{ASANA_BASE}/tasks/{task_gid}",
        json={"data": {"notes": notes}},
        headers=headers,
    )
    r.raise_for_status()
    return r.json()["data"]


def assemble_subtask_notes(
    background: str,
    summary: str,
    done_when: str,
    pillar: str | None = None,
    department: str | None = None,
    assignee: str | None = None,
    status: str | None = "assigned",
) -> str:
    """Build Asana task notes per issue-story-planner v1.1+ / asana-buddy SKILL."""
    bg = background.strip()
    sm = summary.strip()
    dw = done_when.strip()
    parts: list[str] = []
    if department and department.strip():
        parts.append(f"{DEPT_LINE_WRITE}: {department.strip()}")
    if assignee and assignee.strip():
        parts.append(f"担当: {assignee.strip()}")
    if status and status.strip():
        parts.append(f"状態: {status.strip()}")
    if pillar and pillar.strip():
        parts.append(f"柱: {pillar.strip()}")
    header = "\n".join(parts)
    body = f"## 背景\n{bg}\n\n## 概要\n{sm}\n\n## 完了条件\n{dw}"
    return f"{header}\n\n{body}".strip()


def notes_from_legacy_body(body: str, pillar: str | None = None) -> str:
    """Map (title, body, pillar) programs to v1.1 notes layout.

    If body already contains ``## 背景``, only prepend optional ``柱:`` line.
    Otherwise treat body as summary with short background / done_when wrappers.
    """
    body = body.strip()
    if "## 背景" in body:
        if pillar and pillar.strip():
            return f"柱: {pillar.strip()}\n\n{body}"
        return body
    pillar_hint = f"柱「{pillar.strip()}」に関する作業。" if pillar and pillar.strip() else ""
    background = f"本タスクは対策ストーリー上の作業です。{pillar_hint}".strip()
    done_when = "概要の作業が完了し、成果物またはレビュー合意が記録されている。"
    return assemble_subtask_notes(background, body, done_when, pillar=None)


def resolve_project_id(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    for key in ("ASANA_PROJECT_ID", "ASANA_PROJECT_GID", "ASANA_PROJECT"):
        v = os.getenv(key)
        if v:
            return v.strip()
    return None


def resolve_section_id(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    for key in ("ASANA_SECTION_ID", "ASANA_SECTION"):
        v = os.getenv(key)
        if v:
            return v.strip()
    return None


def find_project_task_by_exact_name(project_gid: str, name: str, token: str) -> str | None:
    headers = {"Authorization": f"Bearer {token}"}
    url: str | None = f"{ASANA_BASE}/projects/{project_gid}/tasks"
    params: dict[str, str | int] = {"opt_fields": "name,gid", "limit": 100}
    while url:
        r = requests.get(url, params=params, headers=headers)
        r.raise_for_status()
        body = r.json()
        for t in body.get("data") or []:
            if (t.get("name") or "") == name:
                return str(t["gid"])
        next_page = body.get("next_page") or {}
        url = next_page.get("uri")
        params = {}
    return None


def list_accessible_projects(token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{ASANA_BASE}/users/me",
        params={"opt_fields": "workspaces.gid,workspaces.name"},
        headers=headers,
    )
    r.raise_for_status()
    workspaces = r.json()["data"].get("workspaces") or []
    print("利用可能なプロジェクト（アーカイブ除く）:\n")
    for w in workspaces:
        wgid, wname = w["gid"], w.get("name", "")
        pr = requests.get(
            f"{ASANA_BASE}/projects",
            params={"workspace": wgid, "opt_fields": "name,gid,archived", "limit": 100},
            headers=headers,
        )
        pr.raise_for_status()
        rows = [x for x in pr.json()["data"] if not x.get("archived")]
        print(f"ワークスペース: {wname} ({wgid}) — {len(rows)} 件")
        for p in rows:
            print(f"  {p['gid']}\t{p.get('name', '')}")
        print()


def create_subtask(parent_gid: str, name: str, notes: str, token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"data": {"name": name, "notes": notes, "parent": parent_gid}}
    r = requests.post(f"{ASANA_BASE}/tasks", json=payload, headers=headers)
    r.raise_for_status()
    data = r.json()["data"]
    ensure_subtask_project_membership(data["gid"], parent_gid, token)
    set_assignee_type_org_ops(data["gid"], token)
    return data


def create_subtasks_reversed(
    epic_gid: str,
    items: Sequence[Any],
    token: str,
    notes_for_item: Callable[[Any], str],
    on_created: Callable[[dict], None] | None = None,
) -> None:
    """Create subtasks in reverse order so first list item appears on top in Asana."""
    for item in reversed(items):
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            title = str(item[0])
        elif isinstance(item, dict):
            title = str(item["title"])
        else:
            raise TypeError(f"unsupported subtask item type: {type(item)!r}")
        notes = notes_for_item(item)
        sub = create_subtask(epic_gid, title, notes, token)
        if on_created:
            on_created(sub)
        else:
            print("created_subtask", sub.get("gid"))


def resolve_project_with_fallback(explicit: str | None) -> str:
    project_id = resolve_project_id(explicit)
    if project_id:
        return project_id
    print(
        f"注意: プロジェクトGIDが未指定のためフォールバック {FALLBACK_PROJECT_GID} を使用します。"
        " .env の ASANA_PROJECT_ID または --project の利用を推奨します。",
        file=sys.stderr,
    )
    return FALLBACK_PROJECT_GID


REVIEW_PASSED_STATUSES = frozenset({"passed", "passed_with_notes"})


def load_review_result(path: str) -> dict[str, Any]:
    import json
    from pathlib import Path

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0":
        raise ValueError('review result schema_version must be "1.0"')
    status = data.get("status")
    if status not in REVIEW_PASSED_STATUSES:
        raise ValueError(
            f"review status must be one of {sorted(REVIEW_PASSED_STATUSES)}, got {status!r}"
        )
    if not (data.get("summary") or "").strip():
        raise ValueError("review result summary is required")
    findings = data.get("findings")
    if not isinstance(findings, list):
        raise ValueError("review result findings must be an array")
    for i, item in enumerate(findings):
        if not isinstance(item, dict):
            raise ValueError(f"review result findings[{i}] must be an object")
        for key in ("severity", "category", "message"):
            if not (item.get(key) or "").strip():
                raise ValueError(f"review result findings[{i}].{key} is required")
    high = [f for f in findings if f.get("severity") == "high"]
    if high and status in REVIEW_PASSED_STATUSES:
        print(
            f"警告: status={status!r} だが findings に severity=high が {len(high)} 件。"
            " orchestrator（gate）で差し戻しを検討してください。",
            file=sys.stderr,
        )
    return data


def load_handoff(path: str) -> dict[str, Any]:
    import json
    from pathlib import Path

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    ver = data.get("schema_version")
    if ver not in ("1.1", "1.2"):
        raise ValueError('handoff schema_version must be "1.1" or "1.2"')
    epic = data.get("epic") or {}
    if not epic.get("title") or not epic.get("notes_markdown"):
        raise ValueError("handoff epic.title and epic.notes_markdown are required")
    subtasks = data.get("subtasks")
    if not isinstance(subtasks, list) or not subtasks:
        raise ValueError("handoff subtasks must be a non-empty array")
    for i, st in enumerate(subtasks):
        for key in ("title", "background", "summary", "done_when"):
            if not (st.get(key) or "").strip():
                raise ValueError(f"handoff subtasks[{i}].{key} is required")
    return data


def handoff_subtask_notes(st: dict[str, Any]) -> str:
    return assemble_subtask_notes(
        st["background"],
        st["summary"],
        st["done_when"],
        st.get("pillar"),
        st.get("department"),
    )


_SUBTASK_BRACKET_RE = re.compile(r"【\s*(\d+)\s*/\s*(\d+)\s*")


def parse_subtask_index(name: str, expected_count: int | None = None) -> int | None:
    """Return 0-based subtasks[] index from title 【n/m】, or None."""
    m = _SUBTASK_BRACKET_RE.search(name)
    if not m:
        return None
    n, total = int(m.group(1)), int(m.group(2))
    if n < 1 or total < 1 or n > total:
        return None
    if expected_count is not None and total != expected_count:
        return None
    return n - 1


def sync_handoff_to_parent(
    parent_gid: str,
    handoff: dict[str, Any],
    token: str,
    *,
    update_parent_notes: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Update existing epic notes and sync subtasks (match 【n/m】, fuzzy department, create missing)."""
    expected = handoff["subtasks"]
    expected_count = len(expected)
    headers = {"Authorization": f"Bearer {token}"}
    result: dict[str, Any] = {
        "parent_gid": parent_gid,
        "updated_parent": False,
        "updated": [],
        "created": [],
        "fuzzy_matched": [],
        "unmatched_asana": [],
    }

    if dry_run:
        result["dry_run"] = True
        result["would_update_parent"] = update_parent_notes
        result["subtask_count"] = expected_count
        return result

    if update_parent_notes:
        requests.put(
            f"{ASANA_BASE}/tasks/{parent_gid}",
            json={"data": {"notes": handoff["epic"]["notes_markdown"]}},
            headers=headers,
        ).raise_for_status()
        result["updated_parent"] = True

    asana_tasks = list_subtasks(parent_gid, token)
    used: set[int] = set()
    matched_gids: set[str] = set()

    for t in asana_tasks:
        idx = parse_subtask_index(t["name"], expected_count)
        if idx is None:
            continue
        if idx in used:
            continue
        used.add(idx)
        matched_gids.add(t["gid"])
        st = expected[idx]
        requests.put(
            f"{ASANA_BASE}/tasks/{t['gid']}",
            json={"data": {"name": st["title"], "notes": handoff_subtask_notes(st)}},
            headers=headers,
        ).raise_for_status()
        result["updated"].append({"index": idx + 1, "gid": t["gid"], "title": st["title"]})

    for idx, st in enumerate(expected):
        if idx in used:
            continue
        dept = st.get("department")
        if dept:
            candidates = [
                t
                for t in asana_tasks
                if t["gid"] not in matched_gids
                and parse_subtask_index(t["name"], expected_count) is None
                and parse_task_assignment(t.get("notes") or "").get("department") == dept
            ]
            if len(candidates) == 1:
                t = candidates[0]
                matched_gids.add(t["gid"])
                used.add(idx)
                requests.put(
                    f"{ASANA_BASE}/tasks/{t['gid']}",
                    json={"data": {"name": st["title"], "notes": handoff_subtask_notes(st)}},
                    headers=headers,
                ).raise_for_status()
                result["fuzzy_matched"].append(
                    {"index": idx + 1, "gid": t["gid"], "department": dept, "title": st["title"]}
                )
                continue

        created = create_subtask(parent_gid, st["title"], handoff_subtask_notes(st), token)
        used.add(idx)
        result["created"].append({"index": idx + 1, "gid": created.get("gid"), "title": st["title"]})

    for t in asana_tasks:
        if t["gid"] not in matched_gids:
            result["unmatched_asana"].append({"gid": t["gid"], "name": t["name"]})

    return result
