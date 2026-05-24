#!/usr/bin/env python3
"""Fetch an Asana task and emit an intake snapshot for workflow-orchestrator.

Usage:
  python tools/intake_from_asana.py --task 1215085626249358
  python tools/intake_from_asana.py --task "https://app.asana.com/.../task/1215085626249358"
  python tools/intake_from_asana.py --task <ref> --out output/platform/intake/snapshot.json

Snapshot schema v1.1 adds optional `comments` and `comments_markdown` (user comment stories).

Exit codes: 0 OK · 1 usage/other · 2 invalid ref · 3 Asana API error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
if str(ASANA_OPT) not in sys.path:
    sys.path.insert(0, str(ASANA_OPT))

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import fetch_task, list_task_comment_stories  # noqa: E402

TASK_GID_RE = re.compile(r"/task/(\d+)")
DIGITS_ONLY_RE = re.compile(r"^\d+$")


def parse_task_gid(ref: str) -> str:
    ref = ref.strip()
    if DIGITS_ONLY_RE.match(ref):
        return ref
    m = TASK_GID_RE.search(ref)
    if m:
        return m.group(1)
    raise ValueError(f"cannot extract task GID from: {ref!r}")


def task_url(gid: str) -> str:
    return f"https://app.asana.com/0/0/0/{gid}"


def comments_markdown(comments: list[dict]) -> str:
    if not comments:
        return ""
    blocks: list[str] = []
    for c in comments:
        when = (c.get("created_at") or "").strip()
        author = (c.get("author") or "").strip()
        header = " — ".join(x for x in (when, author) if x) or "comment"
        blocks.append(f"### {header}\n\n{c.get('text', '')}")
    return "\n\n".join(blocks)


def build_snapshot(data: dict, comments: list[dict]) -> dict:
    parent = data.get("parent") or {}
    snapshot: dict = {
        "schema_version": "1.1",
        "task_gid": data.get("gid", ""),
        "task_url": task_url(str(data.get("gid", ""))),
        "name": data.get("name", ""),
        "notes": data.get("notes") or "",
        "completed": bool(data.get("completed")),
        "parent_gid": parent.get("gid") or None,
        "parent_name": parent.get("name") or None,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    if comments:
        snapshot["comments"] = comments
        md = comments_markdown(comments)
        if md:
            snapshot["comments_markdown"] = md
    return snapshot


def main() -> int:
    p = argparse.ArgumentParser(description="Asana task intake snapshot for workflow-orchestrator")
    p.add_argument("--task", required=True, help="Asana task URL or numeric GID")
    p.add_argument("--out", help="Write JSON snapshot to this path (creates parent dirs)")
    p.add_argument(
        "--no-comments",
        action="store_true",
        help="Skip stories fetch (v1.0-compatible output without comments)",
    )
    args = p.parse_args()

    try:
        gid = parse_task_gid(args.task)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    load_env_from_dotfile()
    try:
        token = get_token()
    except SystemExit:
        print("ERROR: ASANA access token not configured (.env)", file=sys.stderr)
        return 3

    try:
        data = fetch_task(gid, token)
        comments: list[dict] = []
        if not args.no_comments:
            comments = list_task_comment_stories(gid, token)
    except Exception as e:  # noqa: BLE001 — CLI boundary
        msg = str(e)
        if "401" in msg or "403" in msg:
            print(
                "ERROR: Asana API denied access — check token and task permissions",
                file=sys.stderr,
            )
        elif "404" in msg:
            print(
                f"ERROR: task {gid} not found — check GID or URL",
                file=sys.stderr,
            )
        else:
            print(f"ERROR: Asana fetch failed: {e}", file=sys.stderr)
        return 3

    if args.no_comments:
        snapshot = build_snapshot(data, [])
        snapshot["schema_version"] = "1.0"
    else:
        snapshot = build_snapshot(data, comments)
    text = json.dumps(snapshot, ensure_ascii=False, indent=2)

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
        print(f"OK wrote {out} comments={len(comments)}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
