# プロジェクト整合性チェック — audit delivery

| 項目 | 内容 |
|------|------|
| epic GID | `1215437556729034` |
| 監査子 GID | `1215437585589944` |
| intake ソース | `1215437323312451` |

## 成果物

- `output/audit/reports/1215437585589944-consistency-audit.json`
- `output/governance/records/1215437557942390-record.md`

## 検証コマンド

```powershell
python tools/validate_org_registry.py
python tools/validate_fixture_schemas.py
python tools/validate_ssot_contract.py
```

## 関連 intake（改善追跡）

- `1215437709736921` — runner RESUME 前 approval_helper 必須化
