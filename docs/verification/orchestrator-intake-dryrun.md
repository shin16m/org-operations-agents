# オーケストレーター入口 workflow ドライラン

## 履歴

| 版 | フロー | 記録 |
|----|--------|------|
| v2 | intake → plan → review → gate → execute | 本ファイル §v2 |
| v3 | intake → bootstrap → dispatch → planning-delivery | [`docs/e2e/default-workflow.md`](../e2e/default-workflow.md) |

---

## v3（現行）

企画チーム L3 化後の手順は [`docs/e2e/default-workflow.md`](../e2e/default-workflow.md) を参照。

| # | step | スキル | 確認内容 |
|---|------|--------|----------|
| 1 | intake | workflow-orchestrator | 生課題 → bootstrap Handoff 生成 |
| 2 | bootstrap | asana-buddy | 親 + 企画子 1 件作成 |
| 3 | dispatch | task-dispatcher | planning-pm へ委譲 |
| 4 | handoff_plan | issue-story-planner | Handoff v1.1 保存 |
| 5 | plan_review | plan-reviewer | `PlanReviewResult` passed* |
| 6 | pm_gate | planning-pm | 人間承認 |
| 7 | asana_execute | asana-buddy | `handoff_to_asana.py --require-review-result` |
| 8 | pm_complete | planning-pm | comment → complete → DeptWorkComplete |

---

## v2（履歴・2026-05-17）

workflow v2: **intake → plan → review → gate → execute**

### 前提

- [`workflows/default.yaml`](../../workflows/default.yaml) `version: "2"`（v3 で置換）
- [`docs/design/workflow-session-io.md`](../design/workflow-session-io.md)

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
- 参照 Handoff: [`handoff.orchestrator-intake-entry.json`](../../skills/planning/issue-story-planner/examples/handoff.orchestrator-intake-entry.json)
