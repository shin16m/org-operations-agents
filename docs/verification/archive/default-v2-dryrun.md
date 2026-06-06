# E2E ドライラン記録 — default v2（履歴）

> **現行:** v3 は [`../cross-team/e2e-dryrun.md`](../cross-team/e2e-dryrun.md) · 手順 [`../../e2e/default-workflow.md`](../../e2e/default-workflow.md)

## 実施日

- 2026-05-17 — マルチエージェント基盤エピック
- 2026-05-17 — workflow v2（orchestrator intake）・スキルレビュー是正

## スコープ（v2）

| 段階 | 確認内容 |
|------|----------|
| intake | workflow-orchestrator → planner 委譲プロンプト |
| plan | issue-story-planner → Handoff v1.1 |
| review | plan-reviewer → PlanReviewResult v1.0 |
| gate | workflow-orchestrator → execute 委譲 |
| execute | handoff_to_asana.py（任意 `--require-review-result`） |

## Asana エピック（参考）

- 基盤構築: https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1214879346897459
- オーケストレーター入口化: https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1214873888809993

## 結果（当時）

- intake 起点 v2 手順で再現可能だった（v3 移行後は非推奨）
- `handoff_to_asana.py --require-review-result` で review ゲートを CLI 強制可能
- レガシー `skills/platform/agent-creater/agents/asana-buddy/` 削除済み
