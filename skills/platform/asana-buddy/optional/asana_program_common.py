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

# Agent Type enum CF（旧称 担当種別 · プロジェクト 1214771428861230 · override via .env）
DEFAULT_ASSIGNEE_TYPE_FIELD_GID = "1215082835199209"
DEFAULT_ASSIGNEE_TYPE_AI_GID = "1215082835199211"
DEFAULT_ASSIGNEE_TYPE_HUMAN_GID = "1215082835199210"

DEFAULT_TASK_TYPE_FIELD_GID = "1215089213221082"
DEFAULT_TASK_TYPE_INTAKE_GID = "1215089213221083"
DEFAULT_TASK_TYPE_EPIC_GID = "1215089213221084"

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
    """Return field + enum option GIDs for Agent Type CF, or None if disabled."""
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
    """Set Agent Type custom field to AI or human. Returns True if set."""
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
    """org-ops CLI が作成/更新するタスク → Agent Type AI。"""
    try:
        return set_assignee_type(task_gid, "AI", token)
    except requests.HTTPError as exc:
        print(
            f"警告: Agent Type CF を設定できませんでした task={task_gid}: {exc}",
            file=sys.stderr,
        )
        return False


HUMAN_GATE_MARKERS = ("【レビュー】", "【承認】")


def is_human_gate_task_name(name: str) -> bool:
    n = (name or "").strip()
    return any(n.startswith(marker) for marker in HUMAN_GATE_MARKERS)


def set_assignee_type_human(task_gid: str, token: str) -> bool:
    """Human approval subtasks → Agent Type human."""
    try:
        return set_assignee_type(task_gid, "human", token)
    except requests.HTTPError as exc:
        print(
            f"警告: Agent Type human を設定できませんでした task={task_gid}: {exc}",
            file=sys.stderr,
        )
        return False


def task_type_config() -> dict[str, str] | None:
    """Return field + enum option GIDs for Task Type CF, or None if disabled."""
    if os.getenv("ASANA_TASK_TYPE_DISABLED", "").strip().lower() in ("1", "true", "yes"):
        return None
    field = (
        os.getenv("ASANA_TASK_TYPE_FIELD_GID", "").strip()
        or DEFAULT_TASK_TYPE_FIELD_GID
    )
    intake = (
        os.getenv("ASANA_TASK_TYPE_INTAKE_GID", "").strip()
        or DEFAULT_TASK_TYPE_INTAKE_GID
    )
    epic = (
        os.getenv("ASANA_TASK_TYPE_EPIC_GID", "").strip()
        or DEFAULT_TASK_TYPE_EPIC_GID
    )
    if not field:
        return None
    return {"field_gid": field, "intake_gid": intake, "epic_gid": epic}


def set_task_type(task_gid: str, kind: str, token: str) -> bool:
    """Set Task Type custom field to Intake or Epic. Returns True if set."""
    cfg = task_type_config()
    if not cfg:
        return False
    kind_norm = kind.strip()
    if kind_norm not in ("Intake", "Epic"):
        raise ValueError(f"task type must be 'Intake' or 'Epic', got {kind!r}")
    opt_gid = cfg["intake_gid"] if kind_norm == "Intake" else cfg["epic_gid"]
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.put(
        f"{ASANA_BASE}/tasks/{task_gid}",
        json={"data": {"custom_fields": {cfg["field_gid"]: opt_gid}}},
        headers=headers,
    )
    r.raise_for_status()
    return True


def set_task_type_epic(task_gid: str, token: str) -> bool:
    """org-ops epic create → Task Type Epic."""
    try:
        return set_task_type(task_gid, "Epic", token)
    except requests.HTTPError as exc:
        print(
            f"警告: Task Type Epic を設定できませんでした task={task_gid}: {exc}",
            file=sys.stderr,
        )
        return False


def read_task_type(task_gid: str, token: str) -> str | None:
    """Return Task Type enum name ('Intake' / 'Epic'), or None if unset/disabled."""
    cfg = task_type_config()
    if not cfg:
        return None
    try:
        cfs = get_task_custom_fields(task_gid, token)
    except requests.HTTPError as exc:
        print(
            f"警告: Task Type 読取失敗 task={task_gid}: {exc}",
            file=sys.stderr,
        )
        return None
    cf = cfs.get(cfg["field_gid"])
    if not cf:
        return None
    enum_value = cf.get("enum_value")
    if not enum_value:
        return None
    gid = str(enum_value.get("gid") or "")
    if gid == cfg["epic_gid"]:
        return "Epic"
    if gid == cfg["intake_gid"]:
        return "Intake"
    return (enum_value.get("name") or "").strip() or None


def is_epic_task(task_gid: str, token: str, *, task: dict[str, Any] | None = None) -> bool:
    """True when Task Type=Epic, or parent-less task with at least one subtask."""
    if read_task_type(task_gid, token) == "Epic":
        return True
    data = task if task is not None else fetch_task(task_gid, token)
    if (data.get("parent") or {}).get("gid"):
        return False
    return bool(list_subtasks(task_gid, token))


def org_os_cf_config() -> dict[str, str] | None:
    """Return OS State + Approval Required CF GIDs from env, or None if unset."""
    field = os.getenv("ASANA_OS_STATE_FIELD_GID", "").strip()
    ready = os.getenv("ASANA_OS_STATE_READY_GID", "").strip()
    if not field or not ready:
        return None
    cfg: dict[str, str] = {
        "os_state_field_gid": field,
        "ready_gid": ready,
        "running_gid": os.getenv("ASANA_OS_STATE_RUNNING_GID", "").strip(),
        "waiting_gid": os.getenv("ASANA_OS_STATE_WAITING_GID", "").strip(),
        "done_gid": os.getenv("ASANA_OS_STATE_DONE_GID", "").strip(),
        "approval_field_gid": os.getenv("ASANA_APPROVAL_REQUIRED_FIELD_GID", "").strip(),
        "approval_yes_gid": os.getenv("ASANA_APPROVAL_REQUIRED_YES_GID", "").strip(),
        "approval_no_gid": os.getenv("ASANA_APPROVAL_REQUIRED_NO_GID", "").strip(),
    }
    return cfg


def set_org_os_custom_fields(
    task_gid: str,
    token: str,
    *,
    os_state: str,
    approval_required: str | None = None,
) -> bool:
    """Set OS State (and optionally Approval Required) on an epic task."""
    cfg = org_os_cf_config()
    if not cfg:
        return False
    mapping = {
        "ready": cfg.get("ready_gid"),
        "running": cfg.get("running_gid"),
        "waiting": cfg.get("waiting_gid"),
        "done": cfg.get("done_gid"),
    }
    state_gid = mapping.get(os_state.lower())
    if not state_gid:
        raise ValueError(f"unknown os_state {os_state!r}")
    custom_fields: dict[str, str] = {cfg["os_state_field_gid"]: state_gid}
    if approval_required is not None:
        ap_field = cfg.get("approval_field_gid")
        if ap_field:
            ap_gid = cfg.get("approval_yes_gid") if approval_required.lower() == "yes" else cfg.get("approval_no_gid")
            if ap_gid:
                custom_fields[ap_field] = ap_gid
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.put(
        f"{ASANA_BASE}/tasks/{task_gid}",
        json={"data": {"custom_fields": custom_fields}},
        headers=headers,
    )
    r.raise_for_status()
    return True


def init_epic_os_state(task_gid: str, token: str) -> bool:
    """New epic after bootstrap: OS State=Ready, no suspend reason, Approval Required=No."""
    root = Path(__file__).resolve().parents[4]
    org_os_src = root / "products/org-os/src"
    if org_os_src.is_dir():
        try:
            if str(org_os_src) not in sys.path:
                sys.path.insert(0, str(org_os_src))
            from org_os import syscall  # noqa: WPS433

            syscall.init_epic(task_gid)
            return True
        except Exception as exc:  # noqa: BLE001
            print(
                f"警告: org-os syscall.init_epic 失敗 task={task_gid}: {exc}",
                file=sys.stderr,
            )
    try:
        return set_org_os_custom_fields(task_gid, token, os_state="Ready", approval_required="no")
    except (requests.HTTPError, ValueError) as exc:
        print(
            f"警告: org-os CF を設定できませんでした task={task_gid}: {exc}",
            file=sys.stderr,
        )
        return False


def approval_result_config() -> dict[str, str] | None:
    """Return Approval Result CF GIDs from env, or None if unset.

    Approval Result は承認サブ完了時に人間が OK/NG を選択する enum CF。
    本フィールドの設定は B（承認ヘルパー）で読み取る前提で、A では env 同期のみ用意する。
    """
    field = os.getenv("ASANA_APPROVAL_RESULT_FIELD_GID", "").strip()
    ok_gid = os.getenv("ASANA_APPROVAL_RESULT_OK_GID", "").strip()
    ng_gid = os.getenv("ASANA_APPROVAL_RESULT_NG_GID", "").strip()
    if not field or not ok_gid or not ng_gid:
        return None
    return {"field_gid": field, "ok_gid": ok_gid, "ng_gid": ng_gid}


def human_approver_gid() -> str | None:
    """Return Asana user GID configured as default human approver, or None."""
    val = os.getenv("ASANA_DEFAULT_HUMAN_APPROVER_GID", "").strip()
    return val or None


def assign_user(task_gid: str, user_gid: str, token: str) -> bool:
    """Set Asana standard `assignee` on a task. Returns True on success."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.put(
            f"{ASANA_BASE}/tasks/{task_gid}",
            json={"data": {"assignee": user_gid}},
            headers=headers,
        )
        r.raise_for_status()
        return True
    except requests.HTTPError as exc:
        print(
            f"警告: assignee を設定できませんでした task={task_gid} user={user_gid}: {exc}",
            file=sys.stderr,
        )
        return False


def html_user_mention_tag(user_gid: str) -> str:
    """Asana rich-text @-mention (requires html_text on stories, not plain text)."""
    gid = str(user_gid or "").strip()
    if not gid:
        return ""
    return f'<a data-asana-type="user" data-asana-gid="{gid}"></a>'


def create_task_story_html(task_gid: str, html_text: str, token: str) -> dict[str, Any]:
    """Post a rich-text comment (story) on an Asana task.

    Stories support only: body, strong, em, u, s, code, ol, ul, li, a, blockquote, pre.
    Unsupported tags (e.g. br, p, h2) cause Asana to escape html_text and break @-mentions.
    """
    headers = {"Authorization": f"Bearer {token}"}
    body = (html_text or "").strip()
    if not body.startswith("<body"):
        body = f"<body>{body}</body>"
    r = requests.post(
        f"{ASANA_BASE}/tasks/{task_gid}/stories",
        json={"data": {"html_text": body}},
        headers=headers,
    )
    r.raise_for_status()
    return r.json()["data"]


def get_task_custom_fields(task_gid: str, token: str) -> dict[str, dict]:
    """Return task custom_fields keyed by field_gid.

    Each value is `{"name": <field name>, "enum_value": <enum option dict | None>}`.
    """
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{ASANA_BASE}/tasks/{task_gid}",
        headers=headers,
        params={
            "opt_fields": (
                "custom_fields.gid,custom_fields.name,"
                "custom_fields.enum_value.gid,custom_fields.enum_value.name"
            )
        },
    )
    r.raise_for_status()
    out: dict[str, dict] = {}
    for cf in (r.json().get("data") or {}).get("custom_fields") or []:
        gid = str(cf.get("gid") or "")
        if not gid:
            continue
        out[gid] = {
            "name": (cf.get("name") or "").strip(),
            "enum_value": cf.get("enum_value"),
        }
    return out


def read_approval_result(task_gid: str, token: str) -> str | None:
    """Return Approval Result enum option name ('OK'/'NG'), or None if unset/CF disabled."""
    cfg = approval_result_config()
    if not cfg:
        return None
    try:
        cfs = get_task_custom_fields(task_gid, token)
    except requests.HTTPError as exc:
        print(
            f"警告: Approval Result 読取失敗 task={task_gid}: {exc}",
            file=sys.stderr,
        )
        return None
    cf = cfs.get(cfg["field_gid"])
    if not cf:
        return None
    enum_value = cf.get("enum_value")
    if not enum_value:
        return None
    name = (enum_value.get("name") or "").strip()
    return name or None


def add_task_to_project(task_gid: str, project_gid: str, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        f"{ASANA_BASE}/tasks/{task_gid}/addProject",
        json={"data": {"project": project_gid}},
        headers=headers,
    )
    r.raise_for_status()


def remove_task_from_project(task_gid: str, project_gid: str, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        f"{ASANA_BASE}/tasks/{task_gid}/removeProject",
        json={"data": {"project": project_gid}},
        headers=headers,
    )
    r.raise_for_status()


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


_SECTION_HEADING_RE = re.compile(r"^##\s+(\S+)", re.MULTILINE)


def build_human_comment_body(
    *,
    actions: Sequence[str],
    reason: str | None = None,
    artifacts: Sequence[str] | None = None,
    next_state: str | None = None,
    retrospective: dict[str, str] | None = None,
) -> str:
    """Build markdown body per agent-asana-comment-signature §4–5."""
    parts: list[str] = ["## 実施内容", "\n".join(f"- {a.strip()}" for a in actions if a and str(a).strip())]
    if reason and reason.strip():
        parts.extend(["## 判断・理由", reason.strip()])
    if artifacts:
        artifact_lines = "\n".join(f"- {a}" for a in artifacts if a and str(a).strip())
        if artifact_lines:
            parts.extend(["## 成果物", artifact_lines])
    if next_state and next_state.strip():
        parts.extend(["## 次の状態", next_state.strip()])
    if retrospective:
        retro_lines: list[str] = []
        for key, label in (
            ("went_well", "うまくいった点"),
            ("improve", "改善したい点"),
            ("next_epic", "次エピック候補"),
        ):
            val = (retrospective.get(key) or "").strip()
            if val:
                retro_lines.append(f"- **{label}:** {val}")
        if retro_lines:
            parts.extend(["## レトロスペクティブ", "\n".join(retro_lines)])
    return "\n\n".join(parts)


def _normalize_comment_body(body: str) -> str:
    """Wrap plain one-liners into ## 実施内容; leave structured markdown unchanged."""
    text = (body or "").strip()
    if not text:
        return ""
    if _SECTION_HEADING_RE.search(text):
        return text
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return ""
    if len(lines) == 1:
        line = lines[0]
        if not line.startswith("- "):
            line = f"- {line}"
        return f"## 実施内容\n\n{line}"
    bullet_block = "\n".join(
        ln if ln.startswith("- ") else f"- {ln}" for ln in lines
    )
    return f"## 実施内容\n\n{bullet_block}"


def _body_has_section(body: str, heading: str) -> bool:
    return f"## {heading}" in (body or "")


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
    """Build Asana story: v1.2+ — human block first, agent-work-record signature last."""
    display = agent_display_name(agent)
    human_lines = ["## 依頼者向け", "", f"**担当:** {display}"]
    summary_text = (summary or "").strip()
    if summary_text:
        human_lines.append(f"**要約:** {summary_text}")
    human_lines.append("")
    main = _normalize_comment_body(body or "")
    if main:
        human_lines.append(main)
    elif summary_text:
        human_lines.append(f"## 実施内容\n\n- {summary_text}")
    else:
        human_lines.append("## 実施内容\n\n- 作業が完了しました。")
    if artifacts and not _body_has_section(main, "成果物"):
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


def list_task_comment_stories(task_gid: str, token: str) -> list[dict[str, Any]]:
    """Return user comment stories (excludes system/activity events)."""
    headers = {"Authorization": f"Bearer {token}"}
    rows: list[dict[str, Any]] = []
    offset = None
    while True:
        params: dict[str, Any] = {
            "opt_fields": "text,created_at,created_by.name,resource_subtype,type",
            "limit": 100,
        }
        if offset:
            params["offset"] = offset
        r = requests.get(
            f"{ASANA_BASE}/tasks/{task_gid}/stories",
            headers=headers,
            params=params,
        )
        r.raise_for_status()
        body = r.json()
        for story in body["data"]:
            text = (story.get("text") or "").strip()
            if not text:
                continue
            subtype = (story.get("resource_subtype") or "").strip()
            stype = (story.get("type") or "").strip()
            if subtype != "comment_added" and stype != "comment":
                continue
            author = ((story.get("created_by") or {}).get("name") or "").strip()
            rows.append(
                {
                    "gid": story.get("gid", ""),
                    "text": text,
                    "created_at": story.get("created_at") or "",
                    "author": author or None,
                }
            )
        offset = (body.get("next_page") or {}).get("offset")
        if not offset:
            break
    rows.sort(key=lambda x: x.get("created_at") or "")
    return rows


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


def add_task_dependencies(task_gid: str, dependency_gids: list[str], token: str) -> None:
    """Make task_gid blocked until each dependency_gid is completed."""
    deps = [g for g in dependency_gids if g]
    if not deps:
        return
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        f"{ASANA_BASE}/tasks/{task_gid}/addDependencies",
        json={"data": {"dependencies": deps}},
        headers=headers,
    )
    r.raise_for_status()


def find_active_review_gate_subtask(
    parent_gid: str,
    token: str,
    *,
    marker: str = "【レビュー】",
) -> dict[str, Any] | None:
    matches = [
        s
        for s in list_subtasks(parent_gid, token)
        if (s.get("name") or "").strip().startswith(marker)
    ]
    if not matches:
        return None
    incomplete = [m for m in matches if not m.get("completed")]
    if incomplete:
        return incomplete[-1]
    return matches[-1]


def wire_worker_subs_to_review_gate(
    parent_gid: str,
    token: str,
    *,
    marker: str = "【レビュー】",
) -> dict[str, Any]:
    """Link each non-gate worker subtask to depend on the active review gate subtask."""
    gate = find_active_review_gate_subtask(parent_gid, token, marker=marker)
    if gate is None:
        return {"status": "no_gate", "wired": []}

    gate_gid = str(gate.get("gid") or "")
    wired: list[str] = []
    for sub in list_subtasks(parent_gid, token):
        sub_gid = str(sub.get("gid") or "")
        if not sub_gid or sub_gid == gate_gid:
            continue
        name = (sub.get("name") or "").strip()
        if is_human_gate_task_name(name):
            continue
        try:
            add_task_dependencies(sub_gid, [gate_gid], token)
            wired.append(sub_gid)
        except requests.HTTPError as exc:
            print(
                f"警告: dependency 設定失敗 sub={sub_gid} gate={gate_gid}: {exc}",
                file=sys.stderr,
            )
    return {"status": "ok", "gate_gid": gate_gid, "wired": wired}


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
    """Create a subtask under parent only (no addProject — avoids list/section top-level display)."""
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
        if st.get("department"):
            set_assignee_type_org_ops(created.get("gid", ""), token)
        result["created"].append({"index": idx + 1, "gid": created.get("gid"), "title": st["title"]})

    for t in asana_tasks:
        if t["gid"] not in matched_gids:
            result["unmatched_asana"].append({"gid": t["gid"], "name": t["name"]})

    return result
