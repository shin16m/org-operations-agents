# agent-create-supporter

Git で共有する **Cursor / Copilot 用エージェントスキル**集。課題をプラン化し、レビュー・オーケストレーションを経て Asana にタスク化する。

## スキル一覧

| スキル | 役割 |
|--------|------|
| [`agent-creater`](skills/agent-creater/SKILL.md) | **新規** `skills/<slug>/` の唯一の生成入口 |
| [`workflow-orchestrator`](skills/workflow-orchestrator/SKILL.md) | **課題の入口（intake）** と review 後のゲート（gate） |
| [`issue-story-planner`](skills/issue-story-planner/SKILL.md) | 課題 → ストーリー → Handoff v1.1 |
| [`plan-reviewer`](skills/plan-reviewer/SKILL.md) | Handoff の品質・リスクレビュー |
| [`asana-buddy`](skills/asana-buddy/SKILL.md) | Handoff → Asana タスク |

## 標準 workflow（review 必須）

```
intake → plan → review（必須）→ gate → execute
```

- **入口:** `workflow-orchestrator`（intake）に生課題を渡す
- **review:** `plan-reviewer` は省略不可（人間目視のみでは `review_passed` にならない）
- **gate:** 同 orchestrator を review 後に再び起動（execute 判定）

定義: [`workflows/default.yaml`](workflows/default.yaml) v2 · 登録: [`workflows/agent-registry.yaml`](workflows/agent-registry.yaml)

### 移行

以前は issue-story-planner 先頭だった。**新規依頼は orchestrator（intake）から**開始する（詳細: [`CONTRIBUTING.md`](CONTRIBUTING.md)）。

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

1. [`workflow-orchestrator`](skills/workflow-orchestrator/README.md)（**intake**）に課題を渡し、planner 用プロンプトを得る
2. [`issue-story-planner`](skills/issue-story-planner/SKILL.md) で Handoff JSON を得る
3. **必須:** [`plan-reviewer`](skills/plan-reviewer/SKILL.md) で `PlanReviewResult`（`passed` / `passed_with_notes`）
4. [`workflow-orchestrator`](skills/workflow-orchestrator/SKILL.md)（**gate**）で execute 可否を確認
5. [`handoff_to_asana.py`](skills/asana-buddy/optional/handoff_to_asana.py) で投入:

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\handoff_to_asana.py --handoff .\path\to\handoff.json -y --if-not-exists
```

詳細: [`docs/e2e/default-workflow.md`](docs/e2e/default-workflow.md)

## エピック進行

- 基盤構築: [`handoff.agent-workflow-orchestration.json`](skills/issue-story-planner/examples/handoff.agent-workflow-orchestration.json)
- オーケストレーター入口化: [`handoff.orchestrator-intake-entry.json`](skills/issue-story-planner/examples/handoff.orchestrator-intake-entry.json)

棚卸し: [`docs/inventory/skills-inventory.md`](docs/inventory/skills-inventory.md)

## 貢献

[`CONTRIBUTING.md`](CONTRIBUTING.md)
