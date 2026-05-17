"""Shared helpers for asana-buddy batch programs and handoff JSON import."""
from __future__ import annotations

import os
import sys
from typing import Any, Callable, Sequence


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
        params={"opt_fields": "name,completed,gid"},
    )
    r.raise_for_status()
    return r.json()["data"]


def assemble_subtask_notes(
    background: str,
    summary: str,
    done_when: str,
    pillar: str | None = None,
    department: str | None = None,
) -> str:
    """Build Asana task notes per issue-story-planner v1.1+ / asana-buddy SKILL."""
    bg = background.strip()
    sm = summary.strip()
    dw = done_when.strip()
    parts: list[str] = []
    if department and department.strip():
        parts.append(f"課: {department.strip()}\n")
    if pillar and pillar.strip():
        parts.append(f"柱: {pillar.strip()}\n")
    parts.append(f"## 背景\n{bg}\n\n## 概要\n{sm}\n\n## 完了条件\n{dw}")
    return "\n".join(parts).strip()


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
    return r.json()["data"]


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
