# qa-verifier SKILL

**独立スキル:** product-manager から **サブタスク**として委譲された **動作検証**（QA）。

PM 委譲: [`docs/design/development-pm-assignment.md`](../../../docs/design/development-pm-assignment.md)

コードレビューは **dev-reviewer** が担当。本スキルは実行・受け入れテストに専念する。

## 着手前（必須）

1. `fetch_task.py --gid <task_gid> --show-assignee` で **担当が qa-verifier** であることを確認する。
2. 一致しない場合は作業せず product-manager へエスカレーション。

## 責務

1. 要件定義書・設計書（あれば）・`done_when` を読む
2. 実装成果に対し動作検証を実施
3. **VerificationResult** を出力（`review_kind: verification`）
4. `status: passed*` で PM へ報告。`failed` も PM へ報告（PM が **developer 向け修正サブ**を新規作成 — [`pm-review-rework-ssot.md`](../../../docs/design/pm-review-rework-ssot.md)）
5. 完了前に `comment_task.py`（`--agent qa-verifier`）

## 出力

スキーマ: [`schemas/verification-result.v1.schema.json`](schemas/verification-result.v1.schema.json)

推奨保存: `output/development/reviews/<task_gid>-verification.json`

## やらないこと

- コード静的レビュー（→ dev-reviewer）
- 要件・仕様の主作成（→ requirements-writer）
- 実装（→ developer）

## 起動例

```
qa-verifier: 子タスク GID ○○ の done_when に沿って動作検証し、VerificationResult を返してください。
```
