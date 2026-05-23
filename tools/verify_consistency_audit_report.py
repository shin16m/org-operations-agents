#!/usr/bin/env python3
"""Re-run validate scripts and cross-check ConsistencyAuditReport claims.

Usage:
  python tools/verify_consistency_audit_report.py --report output/audit/reports/<gid>-consistency.json
  python tools/verify_consistency_audit_report.py --report <path> --require-passed

Exit 0 if report matches live validate results and (optionally) status is passed*.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SCRIPTS: list[tuple[str, str]] = [
    ("organization registry", "tools/validate_org_registry.py"),
    ("fixture schemas", "tools/validate_fixture_schemas.py"),
    ("SSOT cross-document contract", "tools/validate_ssot_contract.py"),
]

SCHEMA_PATH = (
    ROOT / "skills/audit/consistency-auditor/schemas/consistency-audit-report.v1.schema.json"
)


def _run_script(rel: str) -> tuple[int, str, str]:
    r = subprocess.run(
        [sys.executable, str(ROOT / rel)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**dict(__import__("os").environ), "PYTHONIOENCODING": "utf-8"},
    )
    out = (r.stdout or "") + (r.stderr or "")
    tail = "\n".join(out.strip().splitlines()[-3:])
    return r.returncode, tail, out


def _validate_schema(data: dict) -> list[str]:
    from jsonschema import Draft202012Validator

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    return [f"{'.'.join(str(p) for p in e.path) or '(root)'}: {e.message}" for e in validator.iter_errors(data)]


def verify_report(path: Path, *, require_passed: bool) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"report not found: {path}"]

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]

    errors.extend(_validate_schema(data))

    reported = {c.get("script"): c for c in data.get("checks", []) if isinstance(c, dict)}
    for _name, script in REQUIRED_SCRIPTS:
        if script not in reported:
            errors.append(f"report missing check for {script!r}")

    for _name, script in REQUIRED_SCRIPTS:
        live_code, _tail, _full = _run_script(script)
        entry = reported.get(script)
        if entry is None:
            continue
        recorded = entry.get("exit_code")
        if recorded != live_code:
            errors.append(
                f"{script}: report exit_code={recorded!r} but live run exit_code={live_code}"
            )

    status = data.get("status")
    all_zero = all(
        reported.get(script, {}).get("exit_code") == 0 for _n, script in REQUIRED_SCRIPTS if script in reported
    )
    if all_zero and status == "failed":
        errors.append("status is failed but all recorded exit_code values are 0")
    if not all_zero and status in ("passed", "passed_with_notes"):
        errors.append(f"status is {status!r} but at least one recorded exit_code is non-zero")

    if require_passed and status not in ("passed", "passed_with_notes"):
        errors.append(f"require-passed: status is {status!r}")

    return errors


def main() -> int:
    p = argparse.ArgumentParser(description="Verify ConsistencyAuditReport against live validates")
    p.add_argument("--report", required=True, type=Path, help="ConsistencyAuditReport JSON path")
    p.add_argument(
        "--require-passed",
        action="store_true",
        help="Fail unless status is passed or passed_with_notes",
    )
    args = p.parse_args()

    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    errors = verify_report(report_path.resolve(), require_passed=args.require_passed)

    if errors:
        print("\nCONSISTENCY AUDIT REPORT VERIFICATION FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"OK - {report_path.relative_to(ROOT)} matches live validate results.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
