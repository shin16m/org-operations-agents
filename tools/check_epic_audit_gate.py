#!/usr/bin/env python3
"""Block parent epic complete when audit child is incomplete (org-governance gate).

Usage:
  python tools/check_epic_audit_gate.py --parent <PARENT_GID>
  python tools/check_epic_audit_gate.py --parent <PARENT_GID> --handoff path/to/handoff.json

Exit 0 if safe to complete parent; 1 if audit gate blocks.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASANA = ROOT / "skills/platform/asana-buddy/optional"
PY = ROOT / ".venv/Scripts/python.exe"
if not PY.is_file():
    PY = Path(sys.executable)


def _run_fetch_list(parent: str) -> list[tuple[str, str, bool]]:
    r = subprocess.run(
        [str(PY), str(ASANA / "fetch_task.py"), "--gid", parent, "--list-subtasks"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**dict(__import__("os").environ), "PYTHONIOENCODING": "utf-8"},
    )
    if r.returncode != 0:
        print(r.stderr or r.stdout, file=sys.stderr)
        sys.exit(2)
    out: list[tuple[str, str, bool]] = []
    for line in r.stdout.splitlines():
        m = re.match(r"\[([ x])\]\s+(\d+)\s+(.+)$", line.strip())
        if m:
            out.append((m.group(2), m.group(3).strip(), m.group(1) == "x"))
    return out


def _fetch_notes(gid: str) -> str:
    r = subprocess.run(
        [str(PY), str(ASANA / "fetch_task.py"), "--gid", gid],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**dict(__import__("os").environ), "PYTHONIOENCODING": "utf-8"},
    )
    if r.returncode != 0:
        return ""
    if "--- notes ---" in r.stdout:
        return r.stdout.split("--- notes ---", 1)[1]
    return r.stdout


def _handoff_requires_audit(handoff_path: Path) -> bool:
    data = json.loads(handoff_path.read_text(encoding="utf-8"))
    for sub in data.get("subtasks", []):
        if sub.get("department") == "audit":
            return True
    return False


def check_gate(*, parent_gid: str, handoff_path: Path | None) -> list[str]:
    errors: list[str] = []
    subs = _run_fetch_list(parent_gid)
    audit_children: list[tuple[str, str, bool]] = []

    for gid, name, done in subs:
        notes = _fetch_notes(gid)
        if re.search(r"チーム:\s*audit\b", notes) or re.search(r"department:\s*audit\b", notes, re.I):
            audit_children.append((gid, name, done))
        elif "監査" in name and ("audit" in notes.lower() or "監査" in notes):
            audit_children.append((gid, name, done))

    requires_audit = _handoff_requires_audit(handoff_path) if handoff_path else False

    if requires_audit and not audit_children:
        errors.append(
            "handoff contains department=audit subtask but parent has no チーム: audit child on Asana"
        )

    if requires_audit or audit_children:
        if not audit_children:
            errors.append("audit gate: expected at least one audit child on parent epic")
        else:
            incomplete = [(g, n) for g, n, d in audit_children if not d]
            if incomplete:
                for gid, name in incomplete:
                    errors.append(f"audit child incomplete: {gid} {name!r}")

    return errors


def main() -> int:
    p = argparse.ArgumentParser(description="Epic audit gate before parent complete")
    p.add_argument("--parent", required=True, help="Parent epic task GID")
    p.add_argument(
        "--handoff",
        type=Path,
        default=None,
        help="Handoff JSON — if it includes department=audit, gate is enforced",
    )
    args = p.parse_args()

    if str(ASANA) not in sys.path:
        sys.path.insert(0, str(ASANA))
    from agent_handler_asana import get_token, load_env_from_dotfile  # noqa: WPS433

    load_env_from_dotfile()
    _ = get_token()

    handoff = None
    if args.handoff:
        handoff = args.handoff if args.handoff.is_absolute() else ROOT / args.handoff
        if not handoff.is_file():
            print(f"handoff not found: {handoff}", file=sys.stderr)
            return 2

    errors = check_gate(parent_gid=args.parent, handoff_path=handoff)
    if errors:
        print("\nEPIC AUDIT GATE BLOCKED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"OK - audit gate clear for parent {args.parent}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
