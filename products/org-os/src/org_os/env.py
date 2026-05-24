"""Load Asana token and org-os CF GIDs from org-ops .env."""
from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_env_path() -> Path:
    override = os.getenv("ORG_OS_ENV_FILE", "").strip()
    if override:
        return Path(override)
    return repo_root() / "skills/platform/asana-buddy/optional/.env"


def load_dotenv(path: Path | None = None) -> None:
    env_path = path or default_env_path()
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = val.strip()


def get_token() -> str:
    load_dotenv()
    token = os.getenv("ASANA_TOKEN", "").strip()
    if not token:
        raise RuntimeError("ASANA_TOKEN not set (skills/platform/asana-buddy/optional/.env)")
    return token


def org_os_cf_config() -> dict[str, str]:
    load_dotenv()
    field = os.getenv("ASANA_OS_STATE_FIELD_GID", "").strip()
    ready = os.getenv("ASANA_OS_STATE_READY_GID", "").strip()
    if not field or not ready:
        raise RuntimeError(
            "org-os CF GIDs missing — run: python tools/sync_org_os_cf_env.py --project <GID> --write -y"
        )
    return {
        "os_state_field_gid": field,
        "ready_gid": ready,
        "running_gid": os.getenv("ASANA_OS_STATE_RUNNING_GID", "").strip(),
        "waiting_gid": os.getenv("ASANA_OS_STATE_WAITING_GID", "").strip(),
        "done_gid": os.getenv("ASANA_OS_STATE_DONE_GID", "").strip(),
        "approval_field_gid": os.getenv("ASANA_APPROVAL_REQUIRED_FIELD_GID", "").strip(),
        "approval_yes_gid": os.getenv("ASANA_APPROVAL_REQUIRED_YES_GID", "").strip(),
        "approval_no_gid": os.getenv("ASANA_APPROVAL_REQUIRED_NO_GID", "").strip(),
    }


def assignee_type_cf_config() -> dict[str, str]:
    """Agent Type CF GIDs for org-os watch filter."""
    load_dotenv()
    field = os.getenv("ASANA_ASSIGNEE_TYPE_FIELD_GID", "1215082835199209").strip()
    ai = os.getenv("ASANA_ASSIGNEE_TYPE_AI_GID", "1215082835199211").strip()
    human = os.getenv("ASANA_ASSIGNEE_TYPE_HUMAN_GID", "1215082835199210").strip()
    if not field or not ai:
        raise RuntimeError(
            "Agent Type CF GIDs missing — run: python tools/sync_assignee_type_env.py --project <GID> --write -y"
        )
    return {"field_gid": field, "ai_gid": ai, "human_gid": human}


def task_type_cf_config() -> dict[str, str]:
    """Task Type CF GIDs for org-os watch filter."""
    load_dotenv()
    field = os.getenv("ASANA_TASK_TYPE_FIELD_GID", "1215089213221082").strip()
    intake = os.getenv("ASANA_TASK_TYPE_INTAKE_GID", "1215089213221083").strip()
    epic = os.getenv("ASANA_TASK_TYPE_EPIC_GID", "1215089213221084").strip()
    if not field or not epic:
        raise RuntimeError(
            "Task Type CF GIDs missing — run: python tools/sync_task_type_env.py --project <GID> --write -y"
        )
    return {"field_gid": field, "intake_gid": intake, "epic_gid": epic}
