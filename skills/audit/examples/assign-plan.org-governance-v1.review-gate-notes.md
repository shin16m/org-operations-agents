## サブタスク一覧

1. **【1/2・監査】機械検証 + ConsistencyAuditReport** — 担当: `consistency-auditor`
   - validate_org_registry · validate_fixture_schemas · validate_ssot_contract を実行し ConsistencyAuditReport を output/audit/rep
2. **【2/2・監査】AuditReviewResult** — 担当: `audit-reviewer`
   - ConsistencyAuditReport を review_kind org_governance でレビュー。

## 依頼者向け

PM が作成したサブタスク構成と担当割り当てを確認してください。
問題なければ **このサブタスクを完了**（完了 = L3b worker dispatch 承認）。

差し戻し: 本サブを未完了のまま、親にコメントで指摘 → PM が assign plan 再作成 → **新しいレビューサブ**を追加（既存サブは undo しない）。

## Asana dependencies

本サブ完了前、各 worker サブは Asana 上 **本サブに依存** します（`addDependencies`）。

## CLI

```powershell
python tools/check_pm_review_gate.py --parent <PM子GID>
```