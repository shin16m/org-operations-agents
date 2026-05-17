# WorkflowSession I/O（オーケストレーター入口）

タスク 1 成果物。workflow 段階 ID は [`workflows/default.yaml`](../../workflows/default.yaml) と同一語彙。

## WorkflowSession（セッション状態・草案）

誘導型運用（Cursor 手動起動）で、オーケストレーターが保持・更新する状態。

| フィールド | 型 | 説明 |
|------------|-----|------|
| `session_id` | string | 任意のセッション識別子（例: UUID または日時） |
| `raw_request` | string | 利用者が intake で渡した生課題（自然言語） |
| `current_step_id` | enum | `intake` \| `plan` \| `review` \| `gate` \| `execute` |
| `handoff_path` | string? | 保存した Handoff JSON のパス |
| `review_result_path` | string? | `PlanReviewResult` JSON のパス |
| `workflow_id` | string | 例: `default` |

## orchestrator の二役

| step id | 役割 | 入力 | 出力（モデル） |
|---------|------|------|----------------|
| `intake` | 課題受付・窓口 | `raw_request` | 次: `plan` への `prompt_snippet` |
| `gate` | ゲート・execute 判定 | Handoff + `PlanReviewResult` | 次: `execute` への `prompt_snippet` または差し戻し |

## 各 step の入出力

| step id | agent | 入力 | 出力 |
|---------|-------|------|------|
| `intake` | workflow-orchestrator | 生課題 | plan 委譲プロンプト |
| `plan` | issue-story-planner | 生課題（orchestrator 経由） | `AsanaBuddyHandoff` v1.1 |
| `review` | plan-reviewer | Handoff 案 | `PlanReviewResult` |
| `gate` | workflow-orchestrator | Handoff + PlanReviewResult | execute 可否・プロンプト |
| `execute` | asana-buddy | 承認済み Handoff | Asana タスク |

## 起動条件

- **intake:** セッション開始時。`current_step_id` は `intake` または未設定。
- **gate:** `review_passed` 満た後。`PlanReviewResult.status` が `passed` / `passed_with_notes`。

生課題のみで orchestrator（intake）を起動できる。plan / review / execute の実処理は各スキルに委譲する。
