## サブタスク一覧

1. **【1/2・governance】SSOT 実装（ssot-implementer）** — 担当: `ssot-implementer`
   - registry · skills · workflow · docs/tools を実装。validate 実行で exit 0 を確認。
2. **【2/2・governance】実装レビュー（governance-reviewer）** — 担当: `governance-reviewer`
   - review_kind: org_meta。GovernanceReviewResult を output/governance/reviews/ に保存。

## 依頼者向け

PM が作成したサブタスク構成と担当割り当てを確認してください。
問題なければ **このサブタスクを完了**（完了 = L3b worker dispatch 承認）。

差し戻し: 本サブを未完了のまま、親にコメントで指摘 → PM が assign plan 再作成 → **新しいレビューサブ**を追加（既存サブは undo しない）。

## CLI

```powershell
python tools/check_pm_review_gate.py --parent <PM子GID>
```