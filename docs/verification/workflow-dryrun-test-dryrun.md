# ワークフロー ドライラン実行テスト — dryrun 記録

| 項目 | 内容 |
|------|------|
| エピック GID | `1215086194952917` |
| ソース GID | `1215082835252577` |
| development 子 | `1215086180961803` |
| 実施日 | 2026-05-24 |

## 目的

Asana タスク URL を和久桶さんに渡した **intake-asana** から bootstrap → 企画 gate → development まで workflow が実行できることを確認する。

## 手順

### 1. intake-asana（snapshot）

```powershell
python tools/intake_from_asana.py --task 1215082835252577 --out output/platform/intake/1215082835252577-snapshot.json
```

### 2. bootstrap

- Handoff: `output/planning/handoff/bootstrap.workflow-dryrun-test.json`
- `handoff_to_asana.py -y` → 親 `1215086194952917` + 企画子 `1215086237962109`
- `close_intake_source_task.py --source 1215082835252577 --epic 1215086194952917 -y`

### 3. 企画

- Handoff: `handoff.workflow-dryrun-test.json`
- PlanReview: `passed_with_notes`
- gate 承認後 asana_execute → development 子 `1215086180961803`

### 4. development（doc-only）

- `pm_assign_subtasks` + `pm_review_gate`（レビューサブ `1215086180610513`）
- validate 実行（本記録作成時点）

## validate 結果

```powershell
python tools/validate_org_registry.py      # OK
python tools/validate_ssot_contract.py     # OK
python tools/validate_fixture_schemas.py   # OK - 22 fixture(s)
```

## 所見

- intake-asana → bootstrap → 企画 gate → asana_execute まで同一セッションで到達
- `warn_section_add_failed` は親・子作成後に recovery_hint 表示（重複親なし）
- `create_pm_review_gate.py` の `args.yes` バグを `args.y` に修正して PM review gate 作成可能
- PM review gate 承認後 L3b worker dispatch 可能

## 参照

- [`orchestrator-intake-dryrun.md`](orchestrator-intake-dryrun.md)
- [`asana-task-intake-dryrun.md`](asana-task-intake-dryrun.md)
- [`pm-assign-review-gate.md`](../design/pm-assign-review-gate.md)
