## サブタスク一覧

1. **【1/5-1・開発】要件定義（requirements-writer）** — 担当: `requirements-writer`
   - mode=requirements。`output/development/requirements/1215087416996784-requirements.md` に Phase 4 I/O · 検出条件 · 二経路 · 安全弁 · 
2. **【1/5-2・開発】要件 review（dev-reviewer）** — 担当: `dev-reviewer`
   - review_kind: requirements。DocReviewResult を output/development/reviews/ に出力。
3. **【1/5-3・開発】SSOT 実装（developer）** — 担当: `developer`
   - `docs/design/asana-driven-ops.md` Phase 4 節追加 · `workflow-io-contract.md` cross-ref · poller 語彙 `DISPATCH` 案。
4. **【1/5-4・開発】doc review（dev-reviewer）** — 担当: `dev-reviewer`
   - review_kind: code（doc-only 変更）。CodeReviewResult を出力。
5. **【1/5-5・開発】validate 検証（qa-verifier）** — 担当: `qa-verifier`
   - review_kind: verification。validate 3 本 + validate_ssot_contract。

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