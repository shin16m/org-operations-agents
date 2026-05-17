# agent-create-supporter

Git で共有する **Cursor / Copilot 用エージェントスキル**集。課題をプラン化し、レビュー・オーケストレーションを経て Asana にタスク化する。

## スキル一覧

| スキル | 役割 |
|--------|------|
| [`agent-creater`](skills/agent-creater/SKILL.md) | **新規** `skills/<slug>/` の唯一の生成入口 |
| [`issue-story-planner`](skills/issue-story-planner/SKILL.md) | 課題 → ストーリー → Handoff v1.1 |
| [`plan-reviewer`](skills/plan-reviewer/SKILL.md) | Handoff の品質・リスクレビュー |
| [`workflow-orchestrator`](skills/workflow-orchestrator/SKILL.md) | workflow / registry に基づく段階案内 |
| [`asana-buddy`](skills/asana-buddy/SKILL.md) | Handoff → Asana タスク |

## 推奨 workflow

```
plan → review → orchestrate → execute
```

定義: [`workflows/default.yaml`](workflows/default.yaml) · 登録: [`workflows/agent-registry.yaml`](workflows/agent-registry.yaml)

## セットアップ

```powershell
.\skills\asana-buddy\optional\setup_venv.ps1
```

`skills/asana-buddy/optional/.env`:

```env
ASANA_TOKEN=...
ASANA_PROJECT_ID=...
```

## クイックスタート（Asana 投入）

1. [`issue-story-planner`](skills/issue-story-planner/SKILL.md) で Handoff JSON を得る
2. （推奨）[`plan-reviewer`](skills/plan-reviewer/SKILL.md) でレビュー
3. [`handoff_to_asana.py`](skills/asana-buddy/optional/handoff_to_asana.py) で投入:

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\handoff_to_asana.py --handoff .\path\to\handoff.json -y --if-not-exists
```

詳細: [`docs/e2e/default-workflow.md`](docs/e2e/default-workflow.md)

## エピック進行

基盤構築の設計・タスク分解: [`skills/issue-story-planner/examples/handoff.agent-workflow-orchestration.json`](skills/issue-story-planner/examples/handoff.agent-workflow-orchestration.json)

棚卸し: [`docs/inventory/skills-inventory.md`](docs/inventory/skills-inventory.md)

## 貢献

[`CONTRIBUTING.md`](CONTRIBUTING.md)
