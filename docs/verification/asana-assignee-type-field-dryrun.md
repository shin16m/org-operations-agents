# Asana 担当種別 CF — dryrun 記録

| エピック | `1215101173313877` |
| development 子 | `1215085934023360` |
| ソース | `1215082835252581` |

## 検証

```powershell
# CF 一覧（プロジェクト）
# GET custom_field_settings → 担当種別 1215082835199209 · AI 1215082835199211 · human 1215082835199210

# create_subtask 経由では CF を付けない（addProject 撤回のため）
# エピック親 create の AI CF は handoff_to_asana で確認
```

## 実装

- `set_assignee_type` / `set_assignee_type_org_ops` in `asana_program_common.py`
- `create_subtask` — **CF 設定なし**（layout-fix 後）
- `handoff_to_asana.py` 親 create 直後に `AI`
- `.env.example` + `docs/design/asana-assignee-type-field.md`

## 参照

- SSOT: [`docs/design/asana-assignee-type-field.md`](../design/asana-assignee-type-field.md)
