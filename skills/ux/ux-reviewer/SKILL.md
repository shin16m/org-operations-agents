# ux-reviewer SKILL

**独立スキル:** ux-pm または **product-manager**（`full-ui`）から委譲された **UX レビュー**。

人間向け: [`README.md`](README.md) · スキーマ: [`schemas/ux-review-result.v1.schema.json`](schemas/ux-review-result.v1.schema.json)

## review_kind

| kind | 委譲元 | 対象 |
|------|--------|------|
| `ux_spec` | ux-pm | 体験設計書・Design System |
| `ux_implementation` | product-manager | 実装 UI が UX 仕様と一致 |

## 責務

1. 対象成果物を読む（`## 依存` の UX artifact または実装 URL/スクリーンショット）
2. `UxReviewResult` JSON を `output/ux/reviews/` に保存
3. `status: failed` 時:
   - `ux_spec` → ux-designer へ差し戻し
   - `ux_implementation` → product-manager 経由で developer へ修正依頼
4. `comment_task.py` → 委譲元 PM へ報告

## a11y 観点（ux_spec）

- キーボード操作可能性
- コントラスト・フォーカス表示方針
- エラー・空状態の明示

## 起動例

```
ux-reviewer: output/ux/specs/<gid>-ux-spec.md を ux_spec でレビューし、UxReviewResult を出力してください。
```
