## サブタスク一覧

1. **【4/4-1・開発】要件定義（requirements-writer）** — 担当: `requirements-writer`
   - fixture / validate スクリプトへの notes 二層チェック追加要件。
2. **【4/4-2・開発】要件 review（dev-reviewer）** — 担当: `dev-reviewer`
   - review_kind: requirements。DocReviewResult を出力。
3. **【4/4-3・開発】実装（developer）** — 担当: `developer`
   - Handoff fixture・validate_fixture_schemas 更新。
4. **【4/4-4・開発】code review（dev-reviewer）** — 担当: `dev-reviewer`
   - review_kind: code。CodeReviewResult を出力。
5. **【4/4-5・開発】動作検証（qa-verifier）** — 担当: `qa-verifier`
   - validate 3 本が exit 0 であることを確認。
6. **【4/4-6・開発】事後仕様（requirements-writer）** — 担当: `requirements-writer`
   - as-built spec を output/development/specs/ に保存。
7. **【4/4-7・開発】mismatch review（dev-reviewer）** — 担当: `dev-reviewer`
   - review_kind: mismatch。MismatchReviewResult を出力。

## 依頼者向け

PM が作成した検証用サブタスク構成を確認してください。
問題なければ **このサブタスクを完了**（完了 = L3b worker dispatch 承認）。

差し戻し: 本サブを未完了のまま、親にコメントで指摘 → PM が assign plan 再作成 → **新しいレビューサブ**を追加（既存サブは undo しない）。

## Asana dependencies

本サブ完了前、各 worker サブは Asana 上 **本サブに依存** します（`addDependencies`）。

## CLI

```powershell
python tools/check_pm_review_gate.py --parent <PM子GID>
```
