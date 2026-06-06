# オーケストレーター入口 workflow ドライラン（v3）

## 現行手順

[`docs/e2e/default-workflow.md`](../e2e/default-workflow.md) · パイプライン SSOT: [`docs/design/workflow-io-contract.md`](../design/workflow-io-contract.md)

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

## 関連 dryrun

- 企画 L3 化: [`planning-dept-v3-dryrun.md`](../planning/planning-dept-v3-dryrun.md)
- 全チーム: [`all-teams-dryrun.md`](../cross-team/all-teams-dryrun.md)

## 履歴（v2）

v2（L1 完結 plan/review/gate/execute）の記録: [`archive/orchestrator-intake-v2-dryrun.md`](archive/orchestrator-intake-v2-dryrun.md)
