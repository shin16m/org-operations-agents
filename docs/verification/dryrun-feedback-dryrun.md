# ドライラン運用フィードバック — dryrun 記録

| 項目 | 内容 |
|------|------|
| エピック GID | `1215086482130476` |
| ソース GID | `1215082835252617` |
| 関連 dryrun | `1215086194952917` |
| 実施日 | 2026-05-24 |

## フィードバック対応

| ID | 対策 |
|----|------|
| F1 | `pm-assign-review-gate.md` v1.1 — assign **後** review を明確化。dispatch-prompt 全 PM 節に停止ステップ追加 |
| F2 | execution PM 子・handoff department 子に担当種別 `AI`（PUT のみ）。承認サブに `human` |
| F3 | `complete_task.py` が【レビュー】/【承認】サブで exit 3。cursor rule / PM assignment に禁止追記 |

## validate

```powershell
python tools/validate_org_registry.py      # OK
python tools/validate_ssot_contract.py     # OK
python tools/validate_fixture_schemas.py   # OK
```

## CLI smoke

```powershell
# 人間ゲート拒否（exit 3）
python skills/platform/asana-buddy/optional/complete_task.py --gid <【レビュー】サブGID> -y

# PM review gate
python tools/create_pm_review_gate.py --parent <PM子GID> --plan output/development/assign-plans/<plan>.json -y
python tools/check_pm_review_gate.py --parent <PM子GID>
```

## 参照

- [`pm-assign-review-gate.md`](../design/pm-assign-review-gate.md)
- [`asana-assignee-type-field.md`](../design/asana-assignee-type-field.md)
