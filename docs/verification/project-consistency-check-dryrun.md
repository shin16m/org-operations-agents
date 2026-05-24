# プロジェクト整合性チェック — dryrun 記録

| エピック | `1215085684968828` |
| development 子 | `1215085906674344` |
| 実施日 | 2026-05-24 |
| ソース | `1215082835252598` |

## validate 実行結果

```powershell
$env:PYTHONIOENCODING="utf-8"
python tools/validate_org_registry.py      # OK
python tools/validate_ssot_contract.py     # OK
python tools/validate_fixture_schemas.py   # OK - 21 fixture(s)
python tools/check_new_department.py --all # OK - 5 department(s)
```

CI 相当: [`.github/workflows/validate.yml`](../../.github/workflows/validate.yml) と同一 4 本 + check_new_department。

## 検出したドリフトと修正

| 項目 | 状態 | 対応 |
|------|------|------|
| validate 4 本 | すべて exit 0 | 修正不要 |
| `docs/verification/README.md` dryrun 索引 | 直近 4 エピック未掲載 | 索引追加 |
| `docs/verification/README.md` 実行スクリプト | intake/close/backfill/check_new_department 未掲載 | 索引追加 |
| `README.md` スキル一覧 | 監査チーム PM/ワーカー未掲載 | 行追加 |
| `README.md` dispatch 例 | audit 行なし | 行追加 |
| `README.md` クイックスタート | intake-asana 言及なし | 1 行追加 |

## 結論

**機械検証: 不整合なし。** ドキュメント索引・README の記載漏れのみ lite 修正。

## 参照

- [`docs/design/audit-coverage-checks.md`](../design/audit-coverage-checks.md)
