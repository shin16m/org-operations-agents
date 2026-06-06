# governance + audit 整合性チェック — dryrun 記録

| エピック | `1215086493983973` |
| governance 子 | `1215086493983986` |
| audit 子 | `1215086738779538` |
| ソース | `1215086203460977` |
| 実施日 | 2026-05-24 |

## 前回 epic との差分

| 項目 | 前回 `1215086192458137` | 今回 |
|------|-------------------------|------|
| 体制 | governance + audit | 同左（定期再チェック） |
| 確認対象 | governance 新設直後 | PM 運用強化 `1215086341081688` · レトロ intake `1215086241090085` 後 |
| dryrun 索引 | 本ファイル新規時 | `asana-pm-ops-hardening` · `epic-retrospective-intake` 未掲載を修正 |

## validate 実行結果

```powershell
$env:PYTHONIOENCODING="utf-8"
python tools/validate_org_registry.py      # OK - 6 departments
python tools/validate_ssot_contract.py     # OK
python tools/validate_fixture_schemas.py   # OK - 22 fixture(s)
python tools/check_new_department.py --all # OK - 6 department(s)
```

CI 相当: [`.github/workflows/validate.yml`](../../.github/workflows/validate.yml) と同一 4 本 + check_new_department。

## 検出したドリフトと修正

| 項目 | 状態 | 対応 |
|------|------|------|
| validate 4 本 + check_new_department | すべて exit 0 | 修正不要 |
| `docs/verification/README.md` dryrun 索引 | PM 強化・レトロ dryrun 未掲載 | 2 行追加 |
| `docs/verification/README.md` 実行スクリプト | レトロ intake CLI 4 本未掲載 | 索引追加 |
| SSOT / registry / fixture | 不整合なし | 修正不要 |

## 結論

**機械検証: 不整合なし。** ドキュメント索引の記載漏れのみ lite 修正。

## 参照

- [`docs/design/org-improvement-workflow.md`](../design/org-improvement-workflow.md)
- [`docs/design/governance-delivery-io.md`](../design/governance-delivery-io.md)
- [`docs/design/audit-coverage-checks.md`](../design/audit-coverage-checks.md)
- 前回: エピック `1215086192458137`
