# ux-reviewer SKILL

**独立スキル:** ux-pm（**サブタスク**）または **product-manager**（`full-ui`）から委譲された **UX レビュー**。

人間向け: [`README.md`](README.md) · スキーマ: [`schemas/ux-review-result.v1.schema.json`](schemas/ux-review-result.v1.schema.json) · PM 委譲: [`docs/design/ux-pm-assignment.md`](../../../docs/design/ux-pm-assignment.md)

## review_kind

| kind | 委譲元 | 対象 | ゲート |
|------|--------|------|--------|
| **`design_quality`** | ux-pm（サブタスク） | Figma UI の魅力・一貫性・意図の明確さ | `design_quality_passed` |
| `ux_spec` | ux-pm（サブタスク） | ux-spec · Design System · a11y · IA 充足 | `ux_spec_passed` |
| `ux_implementation` | product-manager | 実装 UI が UX 仕様と一致 | development full-ui |

## design_quality の評価観点

| 観点 | 確認内容 |
|------|----------|
| 魅力 | ビジュアルに「これいいな」と感じるか。凡庸なテンプレ感がないか |
| 一貫性 | 画面間・コンポーネント間の統一感 |
| 意図の明確さ | ユーザーが次に何をすべきか視覚的に分かるか |
| DS 準備 | design-system-owner が着手できる粒度か |

`failed` 時: `fix_target: ux_spec`（designer へ差し戻し）

## 着手前（必須）

1. `fetch_task.py --gid <task_gid> --show-assignee` で **担当が ux-reviewer** であることを確認する。
2. 一致しない場合は作業せず委譲元 PM へエスカレーション。

## 責務

1. 対象成果物を読む（Figma URL · UX artifact · 実装 URL/スクリーンショット）
2. `UxReviewResult` JSON を `output/ux/reviews/` に保存
3. `status: failed` 時: `fix_target` を JSON に記載し **委譲元 PM へ報告**
4. **comment_task.py** → 委譲元 PM へ報告

## a11y 観点（ux_spec）

- キーボード操作可能性
- コントラスト・フォーカス表示方針
- エラー・空状態の明示

## 100% polish ゲート（ux_implementation · completion_target: 100）

`full-ui` かつ requirements / 親 notes に `completion_target: 100` があるとき、**ux_implementation** レビューで以下を Must 確認:

| 観点 | failed 例 |
|------|-----------|
| a11y | フォーカス不可 · コントラスト未考慮 |
| エラー UI | API 503 等で無反応 · 技術メッセージ直出し |
| 空状態 | 0 件時に真っ白 · 次アクション無し |

`UxReviewResult` に `polish_checklist_passed: true` を記載。例: [`ux-review-polish-100pct.v1.json`](../../../docs/verification/fixtures/ux/ux-review-polish-100pct.v1.json)

参照: [`delivery-completion-standard.md`](../../../docs/design/delivery-completion-standard.md) v2 · [`ux-delivery-io.md`](../../../docs/design/ux-delivery-io.md) §100% polish

## Asana

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py `
  --gid <GID> --agent ux-reviewer --skill skills/ux/ux-reviewer/SKILL.md --summary "..." --body "..." -y
```

## 起動例

```
あなたは ux-reviewer スキルです。review_kind: design_quality で Figma UI を批評し、
UxReviewResult 出力後に comment_task.py を実行してください。
```
