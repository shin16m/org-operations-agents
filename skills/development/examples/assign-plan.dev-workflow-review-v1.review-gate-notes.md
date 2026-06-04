## サブタスク一覧

1. **【1/4】現状棚卸し・改善要件（requirements-writer）** — 担当: `requirements-writer`
   - 現状 workflow ステップ · 各 slug 責務 · PM/L3b 分離 · 改善案を requirements に記載。
2. **【2/4】要件 review（dev-reviewer）** — 担当: `dev-reviewer`
   - review_kind: requirements。DocReviewResult を reviews 配下に出力。
3. **【3/4】SSOT・SKILL 更新（requirements-writer）** — 担当: `requirements-writer`
   - development-pm-assignment · delivery-io · 代表 SKILL · assign-plan 例を更新。as-built spec 作成。
4. **【4/4】mismatch review（dev-reviewer）** — 担当: `dev-reviewer`
   - review_kind: mismatch。MismatchReviewResult を出力。

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