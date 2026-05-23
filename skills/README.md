# スキル（エージェント）— 組織別レイアウト

各エージェントは **組織フォルダ** 配下に配置する。ペルソナは各 `skills/<organization>/<slug>/personas/` に置く。

| フォルダ | 組織 | 主なエージェント |
|----------|------|------------------|
| [`platform/`](platform/) | **統括グループ** | workflow-orchestrator, asana-buddy, task-dispatcher, agent-creater |
| [`planning/`](planning/) | 企画チーム | planning-pm, issue-story-planner, plan-reviewer |
| [`development/`](development/) | 開発チーム | product-manager, requirements-writer, tech-designer, developer, dev-reviewer, qa-verifier |
| [`analysis/`](analysis/) | 分析チーム | analytics-pm, data-*, ml-engineer, analysis-reviewer |

組織モデル: [`docs/design/department-model.md`](../docs/design/department-model.md)

成果物は [`output/`](../output/) を組織別に参照する。

新規スキル: [`platform/agent-creater/`](platform/agent-creater/) のみが `skills/<organization>/<slug>/` を生成する。

新規**チーム**の追加: [`department-model.md`](../docs/design/department-model.md) の 4 点セット。
