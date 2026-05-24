# エピックサブタスクレビュー運用 — dryrun 記録

| エピック | `1215086194042850` |
| governance brushup 子 | `1215086194108092` |
| governance 実装子 | `1215085956511785` |
| audit 子 | `1215085956479979` |
| ソース | `1215086042051729` |
| 実施日 | 2026-05-24 |

## 成果

### 対策 1: PM 委譲品質ゲート

- 汎用: `create_approval_subtask.py` / `check_approval_subtask.py`
- PM 用: `create_pm_review_gate.py` / `check_pm_review_gate.py`
- design: [`pm-assign-review-gate.md`](../design/pm-assign-review-gate.md)
- workflow: execution 系 5 YAML に `pm_review_gate` 追加

### 対策 2: 企画 → governance ブラッシュアップ

- design: [`planning-governance-brushup.md`](../design/planning-governance-brushup.md)
- workflow: `planning-delivery.yaml` に `plan_brushup`
- 実証: `output/governance/brushup/1215086194108092-brushup.md`

## validate

```powershell
python tools/validate_org_registry.py
python tools/validate_ssot_contract.py
python tools/validate_fixture_schemas.py
python tools/check_new_department.py --all
```

## CLI smoke

```powershell
# PM review gate（assign plan 必須）
python tools/create_pm_review_gate.py --parent <PM子GID> --plan work/assign-plans/example.json --dry-run

python tools/check_pm_review_gate.py --parent <PM子GID>
# exit 2 = 未作成 / 1 = pending / 0 = approved
```

## スコープ外（別エピック）

- planning gate の Asana 化（asana-driven-ops 系と統合）
- エージェント自動 PM 品質向上

## 参照

- [`workflow-io-contract.md`](../design/workflow-io-contract.md)
