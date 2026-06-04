## サブタスク一覧

1. **【3/4-1・開発】要件定義（requirements-writer）** — 担当: `requirements-writer`
   - mode=requirements。`output/development/requirements/<parent_gid>-requirements.md` に変更範囲を記載。
2. **【3/4-2・開発】要件 review（dev-reviewer）** — 担当: `dev-reviewer`
   - review_kind: requirements。DocReviewResult を出力。
3. **【3/4-3・開発】実装（developer）** — 担当: `developer`
   - バグ修正を実装。
4. **【3/4-4・開発】code review（dev-reviewer）** — 担当: `dev-reviewer`
   - review_kind: code。CodeReviewResult を出力。
5. **【3/4-5・開発】動作検証（qa-verifier）** — 担当: `qa-verifier`
   - review_kind: verification。VerificationResult を出力。
6. **【3/4-6・開発】事後仕様（requirements-writer）** — 担当: `requirements-writer`
   - mode=as-built-spec。`output/development/specs/<parent_gid>-spec.md` を作成。
7. **【3/4-7・開発】mismatch review（dev-reviewer）** — 担当: `dev-reviewer`
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