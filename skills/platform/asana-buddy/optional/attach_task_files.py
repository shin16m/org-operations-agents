#!/usr/bin/env python3
"""Upload markdown (or other) files as Asana task attachments.

Usage:
  python attach_task_files.py --gid <WORKER_SUB> --file path/to/doc.md --dry-run
  python attach_task_files.py --gid <WORKER_SUB> --also-gid <REVIEW_SUB> --file a.md -y
  python attach_task_files.py --gid <TASK_GID> --list

Requires ASANA_TOKEN (via .env).
"""
from __future__ import annotations

import argparse
import mimetypes
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import requests  # noqa: E402

from agent_handler_asana import ASANA_BASE, get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import console_safe, fetch_task  # noqa: E402


def list_attachments(task_gid: str, token: str) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{ASANA_BASE}/attachments",
        params={"parent": task_gid, "opt_fields": "name,created_at,download_url,size"},
        headers=headers,
        timeout=60,
    )
    r.raise_for_status()
    return r.json().get("data") or []


def upload_attachment(task_gid: str, file_path: Path, token: str) -> dict:
    if not file_path.is_file():
        raise FileNotFoundError(file_path)
    mime, _ = mimetypes.guess_type(str(file_path))
    if file_path.suffix.lower() == ".md":
        mime = mime or "text/markdown"
    mime = mime or "application/octet-stream"
    headers = {"Authorization": f"Bearer {token}"}
    with file_path.open("rb") as fh:
        r = requests.post(
            f"{ASANA_BASE}/attachments",
            headers=headers,
            files={"file": (file_path.name, fh, mime)},
            data={"parent": task_gid},
            timeout=120,
        )
    r.raise_for_status()
    return r.json()["data"]


def _attachment_names(task_gid: str, token: str) -> set[str]:
    return {str(row.get("name") or "") for row in list_attachments(task_gid, token)}


def upload_files_to_task(
    task_gid: str,
    files: list[Path],
    token: str,
    *,
    skip_if_present: bool = False,
    dry_run: bool = False,
) -> list[dict]:
    """Upload files to one task; optionally skip when basename already attached."""
    uploaded: list[dict] = []
    existing = _attachment_names(task_gid, token) if skip_if_present else set()
    for path in files:
        if skip_if_present and path.name in existing:
            print(f"skip_present  task={task_gid}  name={path.name}")
            continue
        if dry_run:
            print(f"would_upload  task={task_gid}  file={path.name}")
            continue
        data = upload_attachment(task_gid, path, token)
        print(f"uploaded  gid={data.get('gid')}  name={data.get('name')}  file={path.name}")
        uploaded.append(data)
    return uploaded


def main() -> int:
    p = argparse.ArgumentParser(description="Attach local files to an Asana task")
    p.add_argument("--gid", required=True, help="Primary task GID (worker sub)")
    p.add_argument(
        "--also-gid",
        action="append",
        default=[],
        help="Also upload the same file(s) to additional task GID(s) (e.g. review sub)",
    )
    p.add_argument("--file", action="append", default=[], help="File path (repeatable)")
    p.add_argument("--list", action="store_true", help="List existing attachments")
    p.add_argument(
        "--skip-if-present",
        action="store_true",
        help="Skip upload when attachment basename already exists on target task",
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("-y", "--yes", action="store_true")
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()
    task = fetch_task(args.gid, token)
    task_name = str(task.get("name") or args.gid)

    if args.list:
        rows = list_attachments(args.gid, token)
        print(f"ATTACH  task={args.gid}  count={len(rows)}")
        for row in rows:
            print(f"  - {row.get('name')}  size={row.get('size')}")
        return 0

    files = [Path(f).resolve() for f in args.file]
    if not files:
        p.error("at least one --file or --list required")

    for path in files:
        if not path.is_file():
            print(f"ERROR  missing file  {path}", file=sys.stderr)
            return 2

    targets = [args.gid, *args.also_gid]

    if args.dry_run:
        print(f"ATTACH  dry-run  task={args.gid}  name={console_safe(task_name)}")
        for path in files:
            print(f"  would_upload  {path.as_posix()}  bytes={path.stat().st_size}")
        for extra in args.also_gid:
            print(f"  also_target  {extra}")
        return 0

    if not args.yes:
        print(
            console_safe(
                f"タスク {args.gid}"
                + (f" + {len(args.also_gid)} also-gid" if args.also_gid else "")
                + f" に {len(files)} 件添付しますか? (y/N): "
            ),
            end="",
        )
        if input().strip().lower() != "y":
            print("abort")
            return 1

    for target in targets:
        upload_files_to_task(
            target,
            files,
            token,
            skip_if_present=args.skip_if_present,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
