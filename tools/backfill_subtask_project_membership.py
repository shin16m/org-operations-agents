#!/usr/bin/env python3
"""Remove project membership from subtasks that were wrongly addProject'd."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_OPT = _REPO / "skills/platform/asana-buddy/optional"
if str(_OPT) not in sys.path:
    sys.path.insert(0, str(_OPT))

import requests  # noqa: E402

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    ASANA_BASE,
    remove_task_from_project,
    resolve_project_with_fallback,
)


def project_tasks_with_parent(project_gid: str, token: str) -> list[dict]:
    """Tasks in project listing that have a parent = misplaced subtasks."""
    headers = {"Authorization": f"Bearer {token}"}
    rows: list[dict] = []
    offset = None
    while True:
        params: dict = {
            "opt_fields": "name,gid,parent,parent.gid,completed",
            "limit": 100,
        }
        if offset:
            params["offset"] = offset
        r = requests.get(
            f"{ASANA_BASE}/projects/{project_gid}/tasks",
            headers=headers,
            params=params,
        )
        r.raise_for_status()
        body = r.json()
        for t in body["data"]:
            if (t.get("parent") or {}).get("gid"):
                rows.append(t)
        offset = (body.get("next_page") or {}).get("offset")
        if not offset:
            break
    return rows


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--project", default=None)
    p.add_argument("--gid", action="append", default=[], help="Explicit task GID (repeatable)")
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()
    project = resolve_project_with_fallback(args.project)

    if args.gid:
        targets = {gid: {"gid": gid, "name": ""} for gid in args.gid}
    else:
        targets = {t["gid"]: t for t in project_tasks_with_parent(project, token)}

    print(f"project={project} targets={len(targets)}")
    for gid, t in sorted(targets.items()):
        label = (t.get("name") or "")[:70]
        print(f"  {gid}\tcompleted={t.get('completed')}\t{label}")

    if args.dry_run:
        print("dry-run only")
        return

    for gid in sorted(targets):
        remove_task_from_project(gid, project, token)
        print("removed", gid)


if __name__ == "__main__":
    main()
