# ux-reviewer SKILL

**独立スキル:** ux-pm（**サブタスク**）または **product-manager**（`full-ui`）から委譲された **UX レビュー**。

人間向け: [`README.md`](README.md) · スキーマ: [`schemas/ux-review-result.v1.schema.json`](schemas/ux-review-result.v1.schema.json) · PM 委譲: [`docs/design/ux-pm-assignment.md`](../../../docs/design/ux-pm-assignment.md)

## review_kind

| kind | 委譲元 | 対象 |
|------|--------|------|
| `ux_spec` | ux-pm（サブタスク） | 体験設計書・Design System |
| `ux_implementation` | product-manager | 実装 UI が UX 仕様と一致 |

## 着手前（必須）

1. `fetch_task.py --gid <task_gid> --show-assignee` で **担当が ux-reviewer** であることを確認する（`ux_implementation` で development 子の場合も notes の review 委譲を確認）。
2. 一致しない場合は作業せず委譲元 PM へエスカレーション。

## 責務

1. 対象成果物を読む（UX artifact または実装 URL/スクリーンショット）
2. `UxReviewResult` JSON を `output/ux/reviews/` に保存
3. `status: failed` 時:
   - `ux_spec` → ux-designer へ差し戻し（ux-pm がサブ再アサイン）
   - `ux_implementation` → product-manager 経由で developer へ修正依頼
4. **comment_task.py** → 委譲元 PM へ報告

## a11y 観点（ux_spec）

- キーボード操作可能性
- コントラスト・フォーカス表示方針
- エラー・空状態の明示

## Asana

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py `
  --gid <GID> --agent ux-reviewer --skill skills/ux/ux-reviewer/SKILL.md --summary "..." --body "..." -y
```

## 起動例

```
あなたは ux-reviewer スキルです。Asana サブタスク GID ○○ の notes を読み、
担当が ux-reviewer であることを確認してから ux_spec レビューを行い、
UxReviewResult 出力後に comment_task.py を実行してください。
```
