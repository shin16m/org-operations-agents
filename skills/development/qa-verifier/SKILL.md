# qa-verifier SKILL

**独立スキル:** PM / developer から委譲された **動作検証**（QA）。

コードレビューは **dev-reviewer** が担当。本スキルは実行・受け入れテストに専念する。

## 責務

1. 要件定義書・設計書（あれば）・`done_when` を読む
2. 実装成果に対し動作検証を実施
3. **VerificationResult** を出力（`review_kind: verification`）
4. `status: passed` で PM へ報告。`failed` は developer へ差し戻し理由を明記
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
