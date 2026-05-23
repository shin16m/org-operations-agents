#!/usr/bin/env python3
"""Validate Handoff / PlanReviewResult JSON fixtures against JSON Schema.

Run from repo root:
  pip install -r tools/requirements-validate.txt
  python tools/validate_fixture_schemas.py

Exit 0 if OK, 1 on validation errors.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HANDOFF_SCHEMAS: dict[str, Path] = {
    "1.1": ROOT / "skills/planning/issue-story-planner/schemas/asana-buddy-handoff.v1.schema.json",
    "1.2": ROOT / "skills/planning/issue-story-planner/schemas/asana-buddy-handoff.v1.2.schema.json",
}
PLAN_REVIEW_SCHEMA = (
    ROOT / "skills/planning/plan-reviewer/schemas/plan-review-result.v1.schema.json"
)

FIXTURE_GLOBS: list[str] = [
    "docs/verification/fixtures/**/handoff/*.json",
    "docs/verification/fixtures/**/plan-review/*.json",
    "skills/planning/issue-story-planner/examples/handoff*.json",
]


def _load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validator(schema_path: Path):
    from jsonschema import Draft202012Validator

    schema = _load_schema(schema_path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _kind_for_path(path: Path) -> str | None:
    rel = path.as_posix().lower()
    name = path.name.lower()
    if "/handoff/" in rel or name.startswith("handoff.") or name.startswith("bootstrap."):
        return "handoff"
    if "/plan-review/" in rel or name.startswith("plan-review."):
        return "plan_review"
    return None


def _schema_for_handoff(data: dict) -> Path:
    version = str(data.get("schema_version", "1.1")).strip()
    schema_path = HANDOFF_SCHEMAS.get(version)
    if not schema_path:
        raise ValueError(f"unsupported handoff schema_version {version!r}")
    if not schema_path.is_file():
        raise FileNotFoundError(schema_path)
    return schema_path


def validate_instance(path: Path, data: dict, kind: str) -> list[str]:
    from jsonschema import ValidationError

    if kind == "handoff":
        schema_path = _schema_for_handoff(data)
    elif kind == "plan_review":
        schema_path = PLAN_REVIEW_SCHEMA
    else:
        return [f"{path}: unknown fixture kind"]

    validator = _validator(schema_path)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        loc = ".".join(str(p) for p in err.path) or "(root)"
        errors.append(f"{path.relative_to(ROOT)} [{loc}]: {err.message}")
    return errors


def collect_fixture_paths() -> list[Path]:
    seen: set[Path] = set()
    for pattern in FIXTURE_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            if path.is_file():
                seen.add(path.resolve())
    return sorted(seen)


def main() -> int:
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        print(
            "jsonschema is required: pip install -r tools/requirements-validate.txt",
            file=sys.stderr,
        )
        return 1

    errors: list[str] = []
    checked = 0
    for path in collect_fixture_paths():
        kind = _kind_for_path(path)
        if not kind:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON — {exc}")
            continue
        errors.extend(validate_instance(path, data, kind))
        checked += 1

    for schema_path in set(HANDOFF_SCHEMAS.values()) | {PLAN_REVIEW_SCHEMA}:
        if not schema_path.is_file():
            errors.append(f"missing schema file: {schema_path.relative_to(ROOT)}")
        else:
            try:
                _validator(schema_path)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"invalid meta-schema {schema_path.relative_to(ROOT)}: {exc}")

    if errors:
        print("\nFIXTURE SCHEMA VALIDATION FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"OK - {checked} fixture(s) match JSON Schema.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
