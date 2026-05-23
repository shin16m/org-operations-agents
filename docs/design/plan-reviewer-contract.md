# plan-reviewer — レビュー観点と出力スキーマ

タスク 4 成果物。registry エントリ: [`workflows/agent-registry.yaml`](../../workflows/agent-registry.yaml) の `plan-reviewer`。

## 入力

- `AsanaBuddyHandoff` v1.1（`issue-story-planner` 出力）

## 出力: `PlanReviewResult`

機械可読は JSON 1 ブロック。スキーマ: [`skills/planning/plan-reviewer/schemas/plan-review-result.v1.schema.json`](../../skills/planning/plan-reviewer/schemas/plan-review-result.v1.schema.json)

```json
{
  "schema_version": "1.0",
  "status": "passed",
  "summary": "1–2 文の総評",
  "findings": [
    {
      "severity": "high",
      "category": "risk",
      "message": "指摘本文",
      "subtask_index": 2
    }
  ],
  "revised_handoff": null
}
```

### `status` 値

| 値 | 意味 | orchestrator |
|----|------|--------------|
| `passed` | そのまま実行可 | `review_passed` 満たす |
| `passed_with_notes` | 軽微な指摘のみ | `review_passed` 満たす |
| `needs_revision` | 改訂必須 | `review_passed` 未満。`plan` へ差し戻し |
| `blocked` | 重大リスクで停止 | 人間判断 |

### `severity`

`high` | `medium` | `low`

### `category`（観点）

| category | チェック内容 |
|----------|--------------|
| `goal_alignment` | 課題・ストーリー・タスクの目的整合 |
| `risk` | リスク・依存・抜け漏れ |
| `task_granularity` | タスク粒度・着手順 |
| `io_contract` | Handoff v1.1 必須フィールド・schema_version |
| `agent_creater` | 新規スキル実装タスクが agent-creater 委任になっているか |

## 改訂 Handoff

- `needs_revision` 時は `revised_handoff` に完全な `AsanaBuddyHandoff` v1.1 を載せてよい。
- `passed` / `passed_with_notes` 時は `revised_handoff` は省略可（入力 Handoff をそのまま次へ）。

## Handoff との対応（将来）

現状 CLI は review JSON と Handoff JSON の**内容の対応を検証しない**。将来は `PlanReviewResult` に任意フィールド `handoff_meta_title`（`meta.title` と一致）等を載せ、`handoff_to_asana.py` で照合する案。

## 差し戻し条件

- `status` が `needs_revision` または `blocked`
- または `findings` に `severity: high` が 1 件以上（`status` が passed 系でも orchestrator は警告）

## 出力例（passed_with_notes）

```json
{
  "schema_version": "1.0",
  "status": "passed_with_notes",
  "summary": "着手順と完了条件は明確。Asana 投入前にサブタスク 5 の依存を確認推奨。",
  "findings": [
    {
      "severity": "low",
      "category": "risk",
      "message": "タスク 6–7 は agent-creater 前提のため、タスク 5 未完了時はブロックされる。",
      "subtask_index": 5
    }
  ],
  "revised_handoff": null
}
```
