# Analysis delivery v2 — dry-run 実行記録

実施: 2026-06-06 00:49 UTC

## 目的

`analysis-delivery` v2（profile: full）の PM サブタスク分解・**analytics-requirements-writer** 含む全ワーカーが `comment_task` → `complete_task` まで到達することを Asana 上で確認する。

> **API URL:** dryrun 用 stub（`api.example.com`）は実在しません。 下流 consume 契約の形式確認用です。

## 実行

```powershell
$env:PYTHONIOENCODING='utf-8'
tools/run_analysis_v2_dryrun.py
```

## fixture

| 種別 | パス |
|------|------|
| bootstrap | `docs/verification/fixtures/planning/handoff/bootstrap.analysis-v2-dryrun.json` |
| assign plan | `skills/analysis/examples/assign-plan.dryrun-v2.json` |

## Asana

| 項目 | 値 |
|------|-----|
| 親エピック GID | `1215465899468315` |
| 分析子 GID | `1215465899471243` |

## 結果

- workers（順）: analytics-requirements-writer, data-architect, analysis-reviewer, data-engineer, data-steward, data-analyst, data-scientist, ml-engineer, analysis-reviewer, analytics-requirements-writer
- サブタスク数: 10
- analytics-requirements-writer: 要件 + リリースの 2 サブ到達

## stub 成果物

- `output\dryrun\analysis\1215465899471243-requirements.md`
- `output\dryrun\analysis\1215465899471243-catalog.md`
- `output\dryrun\analysis\1215465899471243-model-stub.md`
- `https://api.example.com/dryrun/analysis/v1/predict`

## チェックリスト

- [x] analytics-pm が assign-plan.dryrun-v2.json でサブタスク分解
- [x] analytics-requirements-writer サブが存在（PM 分離）
- [x] 各ワーカーが comment_task → complete
- [x] analytics-pm が親を complete
- [x] stub に API URL を含む（下流 bridge 形式）

## 手動実行

```powershell
python tools/run_analysis_v2_dryrun.py
python tools/run_analysis_v2_dryrun.py --analysis-child <GID> --parent <EPIC_GID>
```

## 関連

- [`analysis-delivery-io.md`](../design/analysis-delivery-io.md)
- [`analytics-pm-assignment.md`](../design/analytics-pm-assignment.md)
- [`cross-team-artifact-bridge.md`](../design/cross-team-artifact-bridge.md)
- [`run_analysis_v2_dryrun.py`](../../tools/run_analysis_v2_dryrun.py)
