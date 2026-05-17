# plan-reviewer SKILL

**独立スキル:** Handoff v1.1 のプラン品質ゲート（`review` スロット・**ワークフロー必須段階**）。新規 `skills/<slug>/` は作成しない → [`agent-creater`](../agent-creater/SKILL.md)。

**省略不可:** 標準 workflow（[`workflows/default.yaml`](../../workflows/default.yaml)）では、Asana 投入前に本スキルによる `PlanReviewResult` が必須。

人間向け手順: [`README.md`](README.md)

## レイアウト

- `SKILL.md` — 本ファイル
- `personas/` — plan_reviewer.json / .md
- 契約: [`docs/design/plan-reviewer-contract.md`](../../docs/design/plan-reviewer-contract.md)
- スキーマ: [`schemas/plan-review-result.v1.schema.json`](schemas/plan-review-result.v1.schema.json)
- registry: [`workflows/agent-registry.yaml`](../../workflows/agent-registry.yaml) の `plan-reviewer`

## 入力

- `AsanaBuddyHandoff` v1.1（[`issue-story-planner`](../issue-story-planner/SKILL.md) 出力）

## 出力

- **`PlanReviewResult`** JSON 1 ブロック（[`plan-reviewer-contract.md`](../../docs/design/plan-reviewer-contract.md)）
- 任意: 改訂 `AsanaBuddyHandoff` v1.1（`revised_handoff` または別ブロック）

## レビュー観点（必須チェック）

| category | 確認内容 |
|----------|----------|
| `goal_alignment` | epic / subtasks が課題・ストーリーと一致 |
| `risk` | 依存・ブロック・抜け漏れ |
| `task_granularity` | 着手順・完了条件の具体性 |
| `io_contract` | v1.1 必須フィールド・非空 |
| `agent_creater` | 新規スキル実装は agent-creater 委任か |

## ゲート

- `passed` / `passed_with_notes` → 下流 [`workflow-orchestrator`（gate）](../workflow-orchestrator/SKILL.md) → [`asana-buddy`](../asana-buddy/SKILL.md) 可
- `needs_revision` / `blocked` → `issue-story-planner` へ差し戻し。Asana 投入不可

## Asana 記録（任意）

レビュー対象タスクの GID が分かる場合、結果提出前に `comment_task.py --agent plan-reviewer` で要約を残してよい。

## 安全

- 外部 API・コマンドは実行しない（利用者が CLI を実行する場合を除く）
- 機密を要求しない

## 起動例

```
あなたは plan-reviewer スキルです。添付 Handoff を PlanReviewResult v1.0 でレビューしてください。
```
