# 分析 → development — 継ぎ目 dryrun

実施: 2026-06-06 01:30 UTC

## 目的

分析子（`profile: model-serve`）完了後、**product-manager が `## 依存` に catalog / model / API URL を転記 → development `profile: full` 着手**までのチーム間継ぎ目を Asana 上で確認する。

> **API URL:** dryrun stub（`api.example.com`）は実在しません。

## 実行

```powershell
$env:PYTHONIOENCODING='utf-8'
.\tools\run_analysis_to_dev_dryrun.py
```

## fixture

| 種別 | パス |
|------|------|
| bootstrap | `docs/verification/fixtures/planning/handoff/bootstrap.analysis-to-dev-dryrun.json` |
| Handoff 例 | `skills/planning/issue-story-planner/examples/handoff.analysis-model-serve.json` |
| 分析 assign plan | `skills/analysis/examples/assign-plan.model-serve-v2.json` |
| 開発 assign plan | `skills/development/examples/assign-plan.analysis-consume-dryrun.json` |

## Asana

| 項目 | GID |
|------|-----|
| 親エピック | `1215466154616864` |
| 分析子（model-serve） | `1215466148596232` |
| 開発子（full） | `1215466148820378` |

## 継ぎ目チェック

- [x] 分析子: model-serve 14 サブ完了 · API URL を artifacts に含む
- [x] 開発子: `## 依存（読み取り専用）` に catalog / model / API URL / SLA
- [x] 開発子: `profile: full` ヘッダのあとに依存表
- [x] API stub: `https://api.example.com/dryrun/analysis-to-dev/v1/predict`
- [x] product-manager が pm_assign 後、開発ワーカーが comment → complete

## 結果

- analysis workers（14）: analytics-requirements-writer, analysis-reviewer, data-architect, analysis-reviewer, data-engineer, analysis-reviewer, data-steward, analysis-reviewer, data-scientist, analysis-reviewer, analysis-reviewer, ml-engineer, analysis-reviewer, analytics-requirements-writer
- dev workers: requirements-writer, dev-reviewer, tech-designer, developer, dev-reviewer, qa-verifier

## 関連

- [`cross-team-artifact-bridge.md`](../design/cross-team-artifact-bridge.md)
- [`handoff.analysis-model-serve.json`](../../skills/planning/issue-story-planner/examples/handoff.analysis-model-serve.json)
- [`analysis-profile-dryrun.md`](../analysis/analysis-profile-dryrun.md)
- [`ux-to-dev-full-ui-dryrun.md`](ux-to-dev-full-ui-dryrun.md)
- [`run_analysis_to_dev_dryrun.py`](../../tools/run_analysis_to_dev_dryrun.py)
