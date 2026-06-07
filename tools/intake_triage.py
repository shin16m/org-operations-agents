#!/usr/bin/env python3
"""Triage intake snapshot → epic_input JSON (L1 extension before bootstrap).

Usage:
  python tools/intake_triage.py --snapshot output/platform/intake/<gid>-snapshot.json
  python tools/intake_triage.py --snapshot ... --out output/platform/triage/<gid>-epic-input.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRIAGE_DIR = ROOT / "output/platform/triage"

INTAKE_PREFIXES = ("【intake】", "【intak】", "[intake]")
SKILL_HINTS: list[tuple[str, tuple[str, ...]]] = [
    ("development", ("実装", "開発", "CLI", "API", "code", "python", "ツール")),
    ("ux", ("UX", "UI", "デザイン", "画面")),
    ("analysis", ("分析", "SLA", "metrics", "計測")),
    ("governance", ("SSOT", "workflow", "registry", "org-meta", "組織")),
    ("audit", ("監査", "audit", "整合")),
    ("planning", ("企画", "Handoff", "planning")),
]


def _strip_intake_prefix(name: str) -> str:
    s = (name or "").strip()
    for p in INTAKE_PREFIXES:
        if s.startswith(p):
            return s[len(p) :].strip()
    return s


def _infer_skill_tags(text: str) -> list[str]:
    found: list[str] = []
    lower = text.lower()
    for tag, keywords in SKILL_HINTS:
        for kw in keywords:
            if kw.lower() in lower or kw in text:
                found.append(tag)
                break
    return found or ["development"]


def _build_description(snapshot: dict) -> str:
    parts: list[str] = []
    notes = (snapshot.get("notes") or "").strip()
    if notes:
        parts.append(notes)
    comments_md = (snapshot.get("comments_markdown") or "").strip()
    if comments_md:
        parts.append("## ソースコメント\n\n" + comments_md)
    return "\n\n".join(parts) if parts else "(no description)"


def _requester_from_snapshot(snapshot: dict) -> str:
    comments = snapshot.get("comments") or []
    if comments:
        return str(comments[0].get("author") or "").strip()
    return ""


def triage_snapshot(snapshot: dict) -> dict:
    gid = str(snapshot.get("task_gid") or "")
    raw_name = (snapshot.get("name") or "intake").strip()
    title = _strip_intake_prefix(raw_name) or raw_name
    text = _build_description(snapshot) + "\n" + raw_name
    priority = str(snapshot.get("priority") or "medium").strip().lower()
    if priority not in ("low", "medium", "high"):
        priority = "medium"

    return {
        "schema_version": "1.0",
        "epic_input": {
            "title": title[:200],
            "description": _build_description(snapshot),
            "priority": priority,
            "skill_tags": _infer_skill_tags(text),
            "metadata": {
                "requester": _requester_from_snapshot(snapshot),
                "source": "intake",
                "source_task_gid": gid,
            },
        },
    }


def epic_title_from_input(epic_input: dict, *, epic_prefix: str = "【org-ops】") -> str:
    title = (epic_input.get("title") or "intake").strip()
    if title.startswith(epic_prefix):
        return title[:120]
    return f"{epic_prefix}{title[:72]}"


_REQUESTER_H2 = re.compile(
    r"^##\s+依頼者向け[^\n]*\n(.*)(?=^##\s|\Z)",
    re.MULTILINE | re.DOTALL,
)
_REQUESTER_SECTION = re.compile(
    r"^##\s+依頼者向け[^\n]*\n.*?(?=^##\s|\Z)",
    re.MULTILINE | re.DOTALL,
)


def _plain_text_requester_summary(description: str, title: str) -> str:
    """First substantive paragraph from free-form intake notes."""
    paragraph: list[str] = []
    for line in (description or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            if paragraph:
                break
            continue
        if not stripped:
            if paragraph:
                break
            continue
        paragraph.append(stripped)
    if paragraph:
        return " ".join(paragraph)[:600]
    clean = (title or "intake").strip()
    return f"intake 課題: **{clean}**"


def _split_requester_from_description(description: str, title: str) -> tuple[str, str]:
    desc = (description or "").strip()
    match = _REQUESTER_H2.search(desc)
    if match:
        requester = match.group(1).strip()
        remainder = _REQUESTER_SECTION.sub("", desc).strip()
        return requester or _plain_text_requester_summary(desc, title), remainder
    return _plain_text_requester_summary(desc, title), desc


def bootstrap_notes_from_epic_input(epic_input: dict, snapshot: dict) -> str:
    """Epic notes for L1 bootstrap — notes-two-layer SSOT (依頼者向け first)."""
    gid = epic_input.get("metadata", {}).get("source_task_gid") or snapshot.get("task_gid")
    url = snapshot.get("task_url") or f"https://app.asana.com/0/0/0/{gid}"
    tags = ", ".join(epic_input.get("skill_tags") or [])
    title = (epic_input.get("title") or snapshot.get("name") or "intake").strip()
    description = epic_input.get("description") or ""
    requester, agent_body = _split_requester_from_description(description, title)

    agent_parts = [
        "### ソース Asana タスク",
        "",
        f"- GID: `{gid}`",
        f"- URL: {url}",
        "",
        "### triage（epic_input）",
        "",
        f"- priority: {epic_input.get('priority')}",
        f"- skill_tags: {tags}",
        "",
    ]
    if agent_body.strip():
        agent_parts.extend(["### intake 原文", "", agent_body.strip(), ""])
    agent_parts.extend(["### 経路", "", "intake → triage → bootstrap", ""])

    return "\n".join(
        [
            "## 依頼者向け（人間が最初に読む）",
            "",
            requester,
            "",
            "## 背景・用語（エージェント / 実装者向け）",
            "",
            "\n".join(agent_parts),
        ]
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Triage intake snapshot to epic_input JSON")
    p.add_argument("--snapshot", required=True, type=Path)
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()

    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    result = triage_snapshot(snapshot)
    gid = snapshot.get("task_gid") or "unknown"
    out = args.out or TRIAGE_DIR / f"{gid}-epic-input.json"
    if not args.out:
        TRIAGE_DIR.mkdir(parents=True, exist_ok=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"TRIAGE  source={gid}  OK  out={out.as_posix()}")
    print(f"  title={result['epic_input']['title'][:60]!r}")
    print(f"  skill_tags={result['epic_input']['skill_tags']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
