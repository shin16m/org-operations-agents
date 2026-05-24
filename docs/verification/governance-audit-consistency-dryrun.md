# governance + audit 整合性チェック — dryrun 記録

| エピック | `1215086192458137` |
| governance 子 | `1215085954851436` |
| audit 子 | `1215086192583071` |
| ソース | `1215101212048272` |
| 実施日 | 2026-05-24 |

## 前回 epic との差分

| 項目 | 前回 `1215085684968828` | 今回 |
|------|-------------------------|------|
| execution 子 | **development** | **governance** + **audit** |
| 担当チーム | 開発 PM ハブ | 組織改善 + 監査（snapshot notes 準拠） |
| dryrun | [`project-consistency-check-dryrun.md`](project-consistency-check-dryrun.md) | 本ファイル |

governance 新設（[`org-improvement-governance-team-dryrun.md`](org-improvement-governance-team-dryrun.md)）後、org-meta 整合性チェックの **実施主体を governance に移管**。

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
| dryrun 記録 | 本 epic 用が未存在 | 本ファイル新規 |
| `docs/verification/README.md` dryrun 索引 | 本 dryrun 未掲載 | 索引追加 |

## 結論

**機械検証: 不整合なし。** governance チーム主体の定期チェックとして記録を残した。

## 参照

- [`docs/design/org-improvement-workflow.md`](../design/org-improvement-workflow.md)
- [`docs/design/governance-delivery-io.md`](../design/governance-delivery-io.md)
- [`docs/design/audit-coverage-checks.md`](../design/audit-coverage-checks.md)
