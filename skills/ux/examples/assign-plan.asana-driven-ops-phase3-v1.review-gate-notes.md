## サブタスク一覧

1. **【1/4-1・UX】Phase 3 体験設計（ux-designer）** — 担当: `ux-designer`
   - ux-spec · approval-ux を Phase 3 向けに更新。`output/ux/specs/1215087283197185-ux-spec.md` と HTML 可読版を作成。
2. **【1/4-2・UX】Phase 3 仕様 review（ux-reviewer）** — 担当: `ux-reviewer`
   - review_kind: ux_spec。`output/ux/reviews/1215087283197185-ux-spec-review.json` を出力。

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