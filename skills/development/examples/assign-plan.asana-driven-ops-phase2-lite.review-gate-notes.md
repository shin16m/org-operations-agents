## サブタスク一覧

1. **【2/4-1・開発】要件定義（requirements-writer）** — 担当: `requirements-writer`
   - mode=requirements。`output/development/requirements/1215087017888498-requirements.md` に変更範囲・受け入れ基準を記載。
2. **【2/4-2・開発】要件 review（dev-reviewer）** — 担当: `dev-reviewer`
   - review_kind: requirements。DocReviewResult を出力。
3. **【2/4-3・開発】実装（developer）** — 担当: `developer`
   - asana_ops_poller / check_workflow_suspend 拡張 · pm_emit_resume_prompt.py 新規 · dryrun doc。
4. **【2/4-4・開発】code review（dev-reviewer）** — 担当: `dev-reviewer`
   - review_kind: code。CodeReviewResult を出力。
5. **【2/4-5・開発】動作検証（qa-verifier）** — 担当: `qa-verifier`
   - review_kind: verification。VerificationResult を出力。

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