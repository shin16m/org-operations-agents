# TaskWork I/O と workflow 拡張（work 段階）

タスク 2 成果物。境界は [`task-execution-boundary.md`](task-execution-boundary.md)。

スキーマ: [`skills/platform/task-executor/schemas/task-work-request.v1.schema.json`](../../skills/platform/task-executor/schemas/task-work-request.v1.schema.json) · [`task-work-result.v1.schema.json`](../../skills/platform/task-executor/schemas/task-work-result.v1.schema.json)

## TaskWorkRequest（実行依頼）

| フィールド | 型 | 説明 |
|------------|-----|------|
| `schema_version` | string | `"1.0"` |
| `task_gid` | string | 実行対象 Asana タスク GID（通常は子タスク） |
| `parent_gid` | string? | 親エピック GID（任意） |
| `locale` | string? | 例: `ja-JP` |

## TaskWorkResult（実行結果）

| フィールド | 型 | 説明 |
|------------|-----|------|
| `schema_version` | string | `"1.0"` |
| `task_gid` | string | 対象タスク |
| `status` | enum | `completed` \| `blocked` \| `needs_tool` |
| `summary` | string | 1–2 文の結果 |
| `artifacts` | string[]? | 作成・更新したファイルパス |
| `delegated_to` | string? | `needs_tool` 時は `agent-creater` 等 |

## WorkflowSession 拡張

| `current_step_id` | 追加 |
|-------------------|------|
| `work` | execute 後、task-executor がサブタスクを実行 |

## workflow 拡張案

- **採用:** [`workflows/with-execution.yaml`](../../workflows/with-execution.yaml) — default v3 の後に `work` 段階を追加
- **default v3:** intake → bootstrap → dispatch（企画は planning-delivery）

```yaml
# with-execution.yaml（要約）
steps:
  - intake → bootstrap → dispatch → work
work:
  agent: task-executor
```

## 利用像

```
… → asana-buddy（execute）→ task-executor（work）→ 完了報告（orchestrator または人）
```
