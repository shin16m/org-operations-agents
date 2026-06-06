# プロジェクト整合性チェック — dryrun 記録

| エピック | `1215087773612736` |
| governance 子 | `1215087773566410` |
| audit 子 | `1215087999196731` |
| ソース intake | `1215086428657865` |
| 実施日 | 2026-05-24 |
| 前回 | `1215085684968828` · [`governance-audit-consistency-dryrun.md`](governance-audit-consistency-dryrun.md) `1215086493983973` |

## validate 実行結果

```powershell
$env:PYTHONIOENCODING="utf-8"
python tools/validate_org_registry.py      # OK - 6 departments
python tools/validate_fixture_schemas.py   # OK - 22 fixture(s)
python tools/validate_ssot_contract.py     # OK
python tools/check_new_department.py --all # OK - 6 department(s)
```

CI 相当: [`.github/workflows/validate.yml`](../../.github/workflows/validate.yml) と同一 4 本 + check_new_department。

## 検出したドリフトと修正

| 項目 | 状態 | 対応 |
|------|------|------|
| validate 4 本 + check_new_department | すべて exit 0 | 修正不要 |
| `docs/verification/README.md` dryrun 索引 | `asana-ops-poller-unicode-dryrun.md` 未掲載 | 索引追加 |
| `docs/design/audit-delivery-io.md` | SSOT 横断整合エピックの audit 必須が不明確 | governance 配賦後 audit を明記 |
| `tools/validate_ssot_contract.py` | `--record-wait` / §H の横断契約なし | 契約 `record-wait orchestrator checklist` 追加 |
| SSOT / registry / fixture 本体 | 不整合なし | 修正不要 |

## 結論

**機械検証: 不整合なし。** 索引漏れ・監査 dispatch 明文化・validate 契約 1 件追加。

## 参照

- [`docs/design/audit-coverage-checks.md`](../design/audit-coverage-checks.md)
- [`docs/design/audit-delivery-io.md`](../design/audit-delivery-io.md)
