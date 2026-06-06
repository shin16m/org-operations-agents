# 組織改善チーム追加 — dryrun 記録

| エピック | `1215085936633800` |
| governance 子 | `1215085954353853` |
| ソース | `1215082835252610` |
| 実施日 | 2026-05-24 |

## 成果

- 新 department `governance`（組織改善チーム）
- `governance-pm` · `ssot-implementer` · `governance-reviewer`
- [`docs/design/org-improvement-workflow.md`](../design/org-improvement-workflow.md)

## validate

```powershell
python tools/validate_org_registry.py
python tools/validate_ssot_contract.py
python tools/validate_fixture_schemas.py
python tools/check_new_department.py --department governance
python tools/check_new_department.py --all
```

## 参照

- [`org-improvement-workflow.md`](../design/org-improvement-workflow.md)
