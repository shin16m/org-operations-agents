# verification/fixtures — 検証用 Handoff JSON

dryrun・smoke 用の **固定 fixture**。実行時の成果物は `output/` へ書き出すが、**git 管理は本ディレクトリのみ**。

| パス | 用途 |
|------|------|
| [`planning/handoff/`](planning/handoff/) | bootstrap / 本番 Handoff |
| [`planning/plan-review/`](planning/plan-review/) | PlanReviewResult |
| [`platform/handoff/`](platform/handoff/) | 統括グループ整備エピック例 |
| [`audit/reports/`](audit/reports/) | ConsistencyAuditReport fixture |
| [`audit/reviews/`](audit/reviews/) | AuditReviewResult fixture |

参照: [`../all-teams-dryrun.md`](../all-teams-dryrun.md) · [`../planning-dept-v3-dryrun.md`](../planning-dept-v3-dryrun.md) · [`../team-label-e2e-dryrun.md`](../team-label-e2e-dryrun.md)

**CI:** `python tools/validate_fixture_schemas.py`（[`tools/requirements-validate.txt`](../../tools/requirements-validate.txt) に `jsonschema`）
