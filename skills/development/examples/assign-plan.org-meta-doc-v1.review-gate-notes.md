## サブタスク一覧

1. **【1/4】要件定義（requirements-writer）** — 担当: `requirements-writer`
   - Handoff 開発子 done_when を requirements に落とす。
2. **【2/4】要件 review（dev-reviewer）** — 担当: `dev-reviewer`
   - review_kind: requirements。DocReviewResult を reviews 配下に出力。
3. **【3/4】事後仕様（requirements-writer）** — 担当: `requirements-writer`
   - mode=as-built-spec。specs 配下に事後仕様。
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