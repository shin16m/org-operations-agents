"""Local and online env validation for org-os setup (doctor command)."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass

import requests

from org_os.env import default_env_path, get_token, load_dotenv

ASANA_BASE = "https://app.asana.com/api/1.0"


def _safe(text: str) -> str:
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        return text.encode(enc, errors="replace").decode(enc, errors="replace")
    except LookupError:
        return text


@dataclass(frozen=True)
class Check:
    key: str
    label: str
    hint_key: str  # lookup in HINT_COMMANDS


HINT_COMMANDS: dict[str, str] = {
    "token": "# .env に ASANA_TOKEN=<your_personal_access_token> を追加",
    "project": (
        "python skills/platform/asana-buddy/optional/handoff_to_asana.py --list-projects"
        "  # 出力 GID を ASANA_PROJECT_ID= に設定"
    ),
    "agent_id": "# .env に ORG_OS_AGENT_ID=wakuoke-local を追加",
    "sync_org_os_cf": "python tools/sync_org_os_cf_env.py --project {project} --write -y",
    "sync_assignee_type": "python tools/sync_assignee_type_env.py --project {project} --write -y",
    "sync_task_type": "python tools/sync_task_type_env.py --project {project} --write -y",
}


# Required env keys grouped for doctor output.
REQUIRED_CHECKS: tuple[Check, ...] = (
    Check("ASANA_TOKEN", "Asana API token", "token"),
    Check("ASANA_PROJECT_ID", "Asana project GID", "project"),
    Check("ORG_OS_AGENT_ID", "org-os agent identity", "agent_id"),
    Check("ASANA_OS_STATE_FIELD_GID", "OS State custom field", "sync_org_os_cf"),
    Check("ASANA_OS_STATE_READY_GID", "OS State / Ready enum", "sync_org_os_cf"),
    Check("ASANA_OS_STATE_RUNNING_GID", "OS State / Running enum", "sync_org_os_cf"),
    Check("ASANA_OS_STATE_WAITING_GID", "OS State / Waiting enum", "sync_org_os_cf"),
    Check("ASANA_OS_STATE_DONE_GID", "OS State / Done enum", "sync_org_os_cf"),
    Check("ASANA_APPROVAL_REQUIRED_YES_GID", "Approval Required / Yes enum", "sync_org_os_cf"),
    Check("ASANA_APPROVAL_REQUIRED_NO_GID", "Approval Required / No enum", "sync_org_os_cf"),
    Check("ASANA_APPROVAL_REQUIRED_FIELD_GID", "Approval Required custom field", "sync_org_os_cf"),
    Check("ASANA_ASSIGNEE_TYPE_FIELD_GID", "Agent Type custom field", "sync_assignee_type"),
    Check("ASANA_ASSIGNEE_TYPE_AI_GID", "Agent Type / AI enum", "sync_assignee_type"),
    Check("ASANA_TASK_TYPE_FIELD_GID", "Task Type custom field", "sync_task_type"),
    Check("ASANA_TASK_TYPE_EPIC_GID", "Task Type / Epic enum", "sync_task_type"),
)


def _project_placeholder() -> str:
    pid = os.getenv("ASANA_PROJECT_ID", "").strip()
    return pid or "<PROJECT_GID>"


def resolve_hint(hint_key: str) -> str:
    template = HINT_COMMANDS.get(hint_key, hint_key)
    return template.format(project=_project_placeholder())


def _present(key: str) -> bool:
    return bool(os.getenv(key, "").strip())


@dataclass
class FailItem:
    key: str
    label: str
    hint_key: str


def run_local_checks() -> tuple[list[str], list[FailItem]]:
    """Return (ok_labels, failures). Loads .env first."""
    load_dotenv()
    ok: list[str] = []
    fail: list[FailItem] = []
    for check in REQUIRED_CHECKS:
        if _present(check.key):
            ok.append(check.label)
        else:
            fail.append(FailItem(check.key, check.label, check.hint_key))
    return ok, fail


def _unique_fix_commands(failures: list[FailItem]) -> list[str]:
    seen: set[str] = set()
    cmds: list[str] = []
    for item in failures:
        cmd = resolve_hint(item.hint_key)
        if cmd not in seen:
            seen.add(cmd)
            cmds.append(cmd)
    return cmds


def doctor_local() -> int:
    """Validate required env keys. Exit 0 if all present, 1 otherwise."""
    env_path = default_env_path()
    print(f"DOCTOR  mode=local  env={env_path}")
    if not env_path.is_file():
        print(f"WARN  .env not found at {env_path}", flush=True)

    ok, fail = run_local_checks()
    for label in ok:
        print(f"  OK  {_safe(label)}")
    for item in fail:
        hint = resolve_hint(item.hint_key)
        print(
            _safe(f"MISSING  {item.key}  ({item.label})"),
            file=sys.stderr,
        )
        print(_safe(f"  FIX  {hint}"), file=sys.stderr)

    if fail:
        print(file=sys.stderr)
        print(_safe("NEXT  run these commands:"), file=sys.stderr)
        for cmd in _unique_fix_commands(fail):
            print(_safe(f"  > {cmd}"), file=sys.stderr)
        print(f"FAIL  {len(fail)} required key(s) missing", file=sys.stderr)
        return 1
    print(f"PASS  {len(ok)} required key(s) present")
    return 0


@dataclass(frozen=True)
class FieldSpec:
    label: str
    match_names: tuple[str, ...]
    field_env: str
    enums: tuple[tuple[str, str], ...]
    hint_key: str


ONLINE_FIELD_SPECS: tuple[FieldSpec, ...] = (
    FieldSpec(
        "OS State",
        ("OS State",),
        "ASANA_OS_STATE_FIELD_GID",
        (
            ("Ready", "ASANA_OS_STATE_READY_GID"),
            ("Running", "ASANA_OS_STATE_RUNNING_GID"),
            ("Waiting", "ASANA_OS_STATE_WAITING_GID"),
            ("Done", "ASANA_OS_STATE_DONE_GID"),
        ),
        "sync_org_os_cf",
    ),
    FieldSpec(
        "Approval Required",
        ("Approval Required",),
        "ASANA_APPROVAL_REQUIRED_FIELD_GID",
        (("Yes", "ASANA_APPROVAL_REQUIRED_YES_GID"), ("No", "ASANA_APPROVAL_REQUIRED_NO_GID")),
        "sync_org_os_cf",
    ),
    FieldSpec(
        "Agent Type",
        ("Agent Type", "agent type", "担当種別"),
        "ASANA_ASSIGNEE_TYPE_FIELD_GID",
        (("AI", "ASANA_ASSIGNEE_TYPE_AI_GID"), ("human", "ASANA_ASSIGNEE_TYPE_HUMAN_GID")),
        "sync_assignee_type",
    ),
    FieldSpec(
        "Task Type",
        ("Task Type", "Task Type (Intake or Epic)", "task type"),
        "ASANA_TASK_TYPE_FIELD_GID",
        (("Intake", "ASANA_TASK_TYPE_INTAKE_GID"), ("Epic", "ASANA_TASK_TYPE_EPIC_GID")),
        "sync_task_type",
    ),
)


@dataclass
class OnlineIssue:
    level: str  # ERROR | WARN
    message: str
    hint_key: str | None = None


def _fetch_project(project_gid: str, token: str) -> dict:
    r = requests.get(
        f"{ASANA_BASE}/projects/{project_gid}",
        headers={"Authorization": f"Bearer {token}"},
        params={"opt_fields": "name,gid"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("data") or {}


def _fetch_project_fields(project_gid: str, token: str) -> dict[str, dict]:
    r = requests.get(
        f"{ASANA_BASE}/projects/{project_gid}/custom_field_settings",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "opt_fields": (
                "custom_field.name,custom_field.gid,"
                "custom_field.enum_options.name,custom_field.enum_options.gid"
            ),
        },
        timeout=30,
    )
    r.raise_for_status()
    by_name: dict[str, dict] = {}
    for row in r.json().get("data") or []:
        cf = row.get("custom_field") or {}
        name = (cf.get("name") or "").strip()
        if not name:
            continue
        opts_by_gid = {
            str(o.get("gid") or ""): (o.get("name") or "").strip()
            for o in (cf.get("enum_options") or [])
        }
        by_name[name.lower()] = {
            "name": name,
            "gid": str(cf.get("gid") or ""),
            "options_by_gid": opts_by_gid,
        }
    return by_name


def _find_field(fields: dict[str, dict], match_names: tuple[str, ...]) -> dict | None:
    for candidate in match_names:
        row = fields.get(candidate.lower())
        if row:
            return row
    return None


def run_online_checks(project_gid: str, token: str) -> list[OnlineIssue]:
    issues: list[OnlineIssue] = []
    try:
        project = _fetch_project(project_gid, token)
    except requests.HTTPError as exc:
        issues.append(
            OnlineIssue(
                "ERROR",
                f"project {project_gid} not reachable ({exc})",
                "project",
            )
        )
        return issues

    print(f"  OK  project exists  {_safe(project.get('name') or project_gid)}")
    fields = _fetch_project_fields(project_gid, token)

    for spec in ONLINE_FIELD_SPECS:
        asana_field = _find_field(fields, spec.match_names)
        env_field_gid = os.getenv(spec.field_env, "").strip()
        if not asana_field:
            issues.append(
                OnlineIssue(
                    "ERROR",
                    f"field {spec.label!r} not found on project (expected one of {spec.match_names})",
                    spec.hint_key,
                )
            )
            continue
        if env_field_gid and env_field_gid != asana_field["gid"]:
            issues.append(
                OnlineIssue(
                    "ERROR",
                    f"{spec.label} field GID mismatch  env={env_field_gid}  asana={asana_field['gid']}",
                    spec.hint_key,
                )
            )
            continue
        print(f"  OK  field {spec.label}  gid={asana_field['gid']}")

        opts = asana_field["options_by_gid"]
        for ssot_name, env_key in spec.enums:
            env_gid = os.getenv(env_key, "").strip()
            if not env_gid:
                issues.append(
                    OnlineIssue("WARN", f"{env_key} not set locally (enum {ssot_name!r})", spec.hint_key)
                )
                continue
            asana_name = opts.get(env_gid)
            if asana_name is None:
                issues.append(
                    OnlineIssue(
                        "ERROR",
                        f"{spec.label} enum GID {env_gid} ({env_key}) not found on Asana",
                        spec.hint_key,
                    )
                )
                continue
            if asana_name != ssot_name:
                issues.append(
                    OnlineIssue(
                        "ERROR",
                        f"{spec.label} enum mismatch  env maps to {asana_name!r}  SSOT expects {ssot_name!r}",
                        spec.hint_key,
                    )
                )
                continue
            print(f"  OK  {spec.label} / {ssot_name}  gid={env_gid}")

        for ssot_name, _env_key in spec.enums:
            if not any(name == ssot_name for name in opts.values()):
                issues.append(
                    OnlineIssue(
                        "WARN",
                        f"{spec.label} missing enum option {ssot_name!r} on Asana project",
                        spec.hint_key,
                    )
                )
    return issues


def doctor_online() -> int:
    """Run local checks then Asana API CF validation. Exit 1 on local/ERROR failures."""
    local_rc = doctor_local()
    if local_rc != 0:
        print(_safe("SKIP  online checks (fix local env first)"), file=sys.stderr)
        return local_rc

    load_dotenv()
    project_gid = os.getenv("ASANA_PROJECT_ID", "").strip()
    if not project_gid:
        print("ERROR  ASANA_PROJECT_ID required for --online", file=sys.stderr)
        return 1

    print(f"DOCTOR  mode=online  project={project_gid}")
    try:
        token = get_token()
    except RuntimeError as exc:
        print(f"ERROR  {exc}", file=sys.stderr)
        return 1

    issues = run_online_checks(project_gid, token)
    errors = [i for i in issues if i.level == "ERROR"]
    warns = [i for i in issues if i.level == "WARN"]

    for issue in issues:
        stream = sys.stderr if issue.level == "ERROR" else sys.stdout
        hint = f"  FIX  {resolve_hint(issue.hint_key)}" if issue.hint_key else ""
        print(_safe(f"{issue.level}  {issue.message}"), file=stream)
        if hint:
            print(_safe(hint), file=stream)

    if errors:
        print(f"FAIL  {len(errors)} online error(s)", file=sys.stderr)
        return 1

    _report_backfill_candidates(project_gid, token)

    if warns:
        print(f"PASS  online checks with {len(warns)} warning(s)")
        return 0
    print("PASS  online checks")
    return 0


def _report_backfill_candidates(project_gid: str, token: str) -> None:
    from org_os.backfill import scan_project

    scan = scan_project(project_gid, token=token)
    n_init = len(scan.init_candidates)
    n_warn = len(scan.warnings)
    if n_init:
        print(_safe(f"  INFO  backfill candidates: {n_init} epic(s) need init_epic"))
        print(
            _safe(
                f"  FIX  python tools/backfill_epic_os_state.py --project {project_gid} --dry-run"
            )
        )
    elif n_warn:
        print(_safe(f"  WARN  backfill: {n_warn} epic(s) have unexpected OS State"))
    else:
        print(_safe("  OK  backfill  no legacy epics need init_epic"))
