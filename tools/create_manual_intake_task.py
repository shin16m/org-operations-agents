#!/usr/bin/env python3
"""Create a single Intake source task from a local notes markdown file.

Usage:
  python tools/create_manual_intake_task.py --notes output/platform/intake/foo-notes.md -y
  python tools/create_manual_intake_task.py --title "short title" --notes path.md -y
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPTIONAL = ROOT / "skills/platform/asana-buddy/optional"
if str(OPTIONAL) not in sys.path:
    sys.path.insert(0, str(OPTIONAL))

from agent_handler_asana import create_task, get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    console_safe,
    resolve_project_with_fallback,
    set_assignee_type_org_ops,
    set_task_type,
)


def main() -> int:
    p = argparse.ArgumentParser(description="Create Asana Intake task from local notes")
    p.add_argument("--notes", type=Path, required=True, help="Markdown body for task notes")
    p.add_argument("--title", default=None, help="Short title (default: notes stem)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("-y", action="store_true")
    args = p.parse_args()

    if not args.notes.is_file():
        print(f"error: notes not found: {args.notes}", file=sys.stderr)
        return 2

    short = (args.title or args.notes.stem.replace("-notes", "")).strip()
    if short.startswith("【intake】"):
        title = short[:120]
    else:
        title = f"【intake】{short[:72]}"
    notes = args.notes.read_text(encoding="utf-8")

    if args.dry_run or not args.y:
        print(console_safe(f"would create  title={title!r}"))
        print(f"  notes={args.notes.as_posix()}  chars={len(notes)}")
        return 0

    load_env_from_dotfile()
    token = get_token()
    project_gid = resolve_project_with_fallback(None)
    task = create_task(project_gid, title, notes, token)
    gid = str(task.get("gid"))
    set_assignee_type_org_ops(gid, token)
    if set_task_type(gid, "Intake", token):
        print("set_task_type_intake", gid)
    url = task.get("permalink_url") or f"https://app.asana.com/0/0/0/{gid}"
    print("created_intake_task", gid, url)
    print(console_safe(f"title={title[:80]}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
