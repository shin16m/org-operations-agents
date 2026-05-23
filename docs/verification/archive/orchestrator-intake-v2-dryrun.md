# オーケストレーター入口 workflow — v2 dryrun（履歴）

> **現行 v3:** [`../orchestrator-intake-dryrun.md`](../orchestrator-intake-dryrun.md) · [`../../e2e/default-workflow.md`](../../e2e/default-workflow.md)

## workflow v2

**intake → plan → review → gate → execute**（L1 完結）

### 前提

- `workflows/default.yaml` `version: "2"`（v3 で置換）
- [`docs/design/workflow-session-io.md`](../../design/workflow-session-io.md)

### 手順（架空課題）

| # | step | スキル | 確認内容 |
|---|------|--------|----------|
| 1 | intake | workflow-orchestrator | 課題 → plan 用 `prompt_snippet` |
| 2 | plan | issue-story-planner | Handoff v1.1 JSON |
| 3 | review | plan-reviewer | PlanReviewResult passed* |
| 4 | gate | workflow-orchestrator | execute 委譲 |
| 5 | execute | asana-buddy | handoff_to_asana.py |

### 結果

- 2026-05-17: intake 起点 v2 手順を文書化。Asana エピック `1214873888809993` と同期。
- 参照 Handoff: [`handoff.orchestrator-intake-entry.json`](../../../skills/planning/issue-story-planner/examples/handoff.orchestrator-intake-entry.json)
