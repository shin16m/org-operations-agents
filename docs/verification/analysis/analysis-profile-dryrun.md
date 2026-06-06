# Analysis profile dryrun — 実行記録

実施: 2026-06-06 01:21 UTC

## 目的

`analysis-delivery` v2 の **insights / catalog / model-serve** profile について、assign plan どおりのサブタスク数・担当 slug が Asana 上で到達することを確認する。

## 実行

```powershell
$env:PYTHONIOENCODING='utf-8'
.\tools\run_analysis_profile_dryrun.py --profile all
```

## 手順（単体）

```powershell
python tools/run_analysis_profile_dryrun.py --profile catalog
python tools/run_analysis_profile_dryrun.py --profile insights
python tools/run_analysis_profile_dryrun.py --profile model-serve
```

## 結果

### profile: `catalog`

- assign plan: `skills/analysis/examples/assign-plan.catalog-v2.json`
- 分析子 GID: `1215466257319661`
- サブタスク数: 7
- workers: analytics-requirements-writer, analysis-reviewer, data-architect, analysis-reviewer, data-steward, analysis-reviewer, analytics-requirements-writer

### profile: `insights`

- assign plan: `skills/analysis/examples/assign-plan.insights-v2.json`
- 分析子 GID: `1215465981837950`
- サブタスク数: 11
- workers: analytics-requirements-writer, analysis-reviewer, data-architect, analysis-reviewer, data-engineer, analysis-reviewer, data-steward, analysis-reviewer, data-analyst, analysis-reviewer, analytics-requirements-writer

### profile: `model-serve`

- assign plan: `skills/analysis/examples/assign-plan.model-serve-v2.json`
- 分析子 GID: `1215466257241360`
- サブタスク数: 14
- workers: analytics-requirements-writer, analysis-reviewer, data-architect, analysis-reviewer, data-engineer, analysis-reviewer, data-steward, analysis-reviewer, data-scientist, analysis-reviewer, analysis-reviewer, ml-engineer, analysis-reviewer, analytics-requirements-writer

## 関連

- [`analysis-delivery-v2-dryrun.md`](analysis-delivery-v2-dryrun.md)（full profile）
- [`analytics-pm-assignment.md`](../design/analytics-pm-assignment.md)
- [`run_analysis_profile_dryrun.py`](../../tools/run_analysis_profile_dryrun.py)
