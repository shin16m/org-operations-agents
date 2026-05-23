# スキル（エージェント）— 組織別レイアウト

各エージェントは **組織（課）フォルダ** 配下に配置する。ペルソナ（利き脳）は各 `skills/<organization>/<slug>/personas/` に置く。

| フォルダ | 組織 | 主なエージェント |
|----------|------|------------------|
| [`platform/`](platform/) | 横断（L1/L2・メタ） | workflow-orchestrator, asana-buddy, task-dispatcher, agent-creater |
| [`planning/`](planning/) | 企画課 | issue-story-planner, plan-reviewer |
| [`development/`](development/) | 開発課 | product-manager, doc-writer, developer, reviewer |
| [`analysis/`](analysis/) | 分析課 | analytics-pm, data-*, ml-engineer, analysis-reviewer |

成果物（Handoff・要件・レビュー JSON 等）は [`output/`](../output/) を組織別に参照する。

新規スキル: [`platform/agent-creater/`](platform/agent-creater/) のみが `skills/<organization>/<slug>/` を生成する。
