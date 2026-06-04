#!/usr/bin/env python3
"""Resolve dev-reviewer review subtask GID under a development PM child.

Usage:
  python tools/resolve_dev_review_sub.py --parent 1215435778230658 --review-kind requirements
  python tools/resolve_dev_review_sub.py --parent 1215435778230658 --review-kind mismatch --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA_OPT = ROOT / "skills/platform/asana-buddy/optional"
if str(ASANA_OPT) not in sys.path:
    sys.path.insert(0, str(ASANA_OPT))

from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import fetch_task, list_subtasks, parse_task_assignment  # noqa: E402

REVIEW_KIND_ALIASES: dict[str, tuple[str, ...]] = {
    "requirements": ("requirements", "要件 review", "要件レビュー"),
    "mismatch": ("mismatch", "mismatch review"),
}


def _notes_review_kind(notes: str) -> str | None:
    m = re.search(r"review_kind:\s*(\w+)", notes, re.I)
    if m:
        return m.group(1).strip().lower()
    lower = notes.lower()
    if "mismatch" in lower:
        return "mismatch"
    if "requirements" in lower or "要件" in notes:
        return "requirements"
    return None


def _name_matches(name: str, review_kind: str) -> bool:
    n = name.lower()
    for alias in REVIEW_KIND_ALIASES.get(review_kind, (review_kind,)):
        if alias.lower() in n:
            return True
    return False


def resolve_review_sub(
    parent_gid: str,
    review_kind: str,
    *,
    token: str,
) -> dict | None:
    kind = review_kind.strip().lower()
    if kind not in REVIEW_KIND_ALIASES:
        raise ValueError(f"review_kind must be one of {sorted(REVIEW_KIND_ALIASES)}, got {review_kind!r}")

    candidates: list[dict] = []
    for sub in list_subtasks(parent_gid, token):
        if sub.get("completed"):
            continue
        name = str(sub.get("name") or "")
        if name.strip().startswith(("【レビュー】", "【承認】")):
            continue
        gid = str(sub["gid"])
        notes = fetch_task(gid, token).get("notes") or ""
        assignee = parse_task_assignment(str(notes)).get("assignee")
        if assignee != "dev-reviewer":
            continue
        nk = _notes_review_kind(str(notes))
        if nk == kind or _name_matches(name, kind):
            candidates.append({"gid": gid, "name": name, "notes_kind": nk})

    if not candidates:
        return None
    # Prefer explicit review_kind in notes over name-only match
    explicit = [c for c in candidates if c.get("notes_kind") == kind]
    row = explicit[0] if explicit else candidates[0]
    return {"review_sub_gid": row["gid"], "name": row["name"], "review_kind": kind}


def main() -> int:
    p = argparse.ArgumentParser(description="Resolve dev-reviewer review subtask GID")
    p.add_argument("--parent", required=True, help="Development PM child task GID")
    p.add_argument(
        "--review-kind",
        required=True,
        choices=sorted(REVIEW_KIND_ALIASES),
    )
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()
    result = resolve_review_sub(args.parent, args.review_kind, token=token)
    if result is None:
        print(
            f"error: no open dev-reviewer sub for review_kind={args.review_kind} "
            f"parent={args.parent}",
            file=sys.stderr,
        )
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["review_sub_gid"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
