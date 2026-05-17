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
| [`task-executor`](skills/task-executor/SKILL.md) | Asana サブタスク実行（work・**過渡期**） |
| [`task-dispatcher`](skills/task-dispatcher/SKILL.md) | 子タスクを課へ配賦（dispatch） |
| [`product-manager`](skills/product-manager/SKILL.md) | 開発課 PM（子 1 件のハブ） |
| [`doc-writer`](skills/doc-writer/SKILL.md) / [`developer`](skills/developer/SKILL.md) / [`reviewer`](skills/reviewer/SKILL.md) | 開発課の委譲ロール |

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
5. [`handoff_to_asana.py`](skills/asana-buddy/optional/handoff_to_asana.py) で投入（**review 強制**）:

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\handoff_to_asana.py `
  --handoff .\path\to\handoff.json `
  --require-review-result .\path\to\review.json `
  -y --if-not-exists
```

`--require-review-result` を省略すると SKILL 上の前提のみ（CI・本番運用では付与を推奨。詳細: [`CONTRIBUTING.md`](CONTRIBUTING.md)）。

詳細: [`docs/e2e/default-workflow.md`](docs/e2e/default-workflow.md)

### タスク化のあと（配賦・開発課）

子タスクごとに **dispatch → 開発課 PM workflow** が走ります（例: 「子タスク GID ○○ を開発課で実行」）。

```
execute → dispatch（task-dispatcher）→ product-manager → doc-writer / developer / reviewer
```

- 推奨: [`workflows/with-dispatch.yaml`](workflows/with-dispatch.yaml) · [`docs/e2e/dispatch-workflow.md`](docs/e2e/dispatch-workflow.md)
- 過渡期（単一ワーカー）: [`workflows/with-execution.yaml`](workflows/with-execution.yaml) + `task-executor`

## エピック進行

- 基盤構築: [`handoff.agent-workflow-orchestration.json`](skills/issue-story-planner/examples/handoff.agent-workflow-orchestration.json)
- オーケストレーター入口化: [`handoff.orchestrator-intake-entry.json`](skills/issue-story-planner/examples/handoff.orchestrator-intake-entry.json)
- スキルレビュー是正: [`handoff.skill-review-remediation.json`](skills/issue-story-planner/examples/handoff.skill-review-remediation.json)
- タスク実行エージェント: [`handoff.task-executor-agent.json`](skills/issue-story-planner/examples/handoff.task-executor-agent.json)
- 組織配賦・PM ワークフロー: [`handoff.org-dispatch-pm-workflow.json`](skills/issue-story-planner/examples/handoff.org-dispatch-pm-workflow.json)

棚卸し: [`docs/inventory/skills-inventory.md`](docs/inventory/skills-inventory.md)

## 貢献

[`CONTRIBUTING.md`](CONTRIBUTING.md)
