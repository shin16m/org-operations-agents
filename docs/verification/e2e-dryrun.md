# E2E ドライラン記録

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

## 中間成果物（パス）

| 段階 | ファイル |
|------|----------|
| 設計 | `docs/inventory/skills-inventory.md` |
| I/O | `docs/design/workflow-io-contract.md` |
| セッション | `docs/design/workflow-session-io.md` |
| registry | `workflows/agent-registry.yaml` |
| workflow | `workflows/default.yaml` v2 |
| review 契約 | `docs/design/plan-reviewer-contract.md` |
| review スキーマ | `skills/planning/plan-reviewer/schemas/plan-review-result.v1.schema.json` |
| E2E 手順 | `docs/e2e/default-workflow.md` |
| 入口化 dryrun | `docs/verification/orchestrator-intake-dryrun.md` |

## Asana エピック（参考）

- 基盤構築: https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1214879346897459
- オーケストレーター入口化: https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1214873888809993

## 拡張スモーク（registry）

- 未登録 slug 参照時、orchestrator SKILL は registry 更新手順を返す（[`workflow-orchestrator/SKILL.md`](../../skills/platform/workflow-orchestrator/SKILL.md)）

## 結果

- ルート README → intake 起点の v2 手順で再現可能
- `handoff_to_asana.py --require-review-result` で review ゲートを CLI 強制可能
- レガシー `skills/platform/agent-creater/agents/asana-buddy/` 削除済み
