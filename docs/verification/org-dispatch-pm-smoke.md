# 組織配賦・開発課 PM — スモーク記録

エピック Handoff: [`handoff.org-dispatch-pm-workflow.json`](../../skills/issue-story-planner/examples/handoff.org-dispatch-pm-workflow.json)

## Asana

| 項目 | GID / URL |
|------|-----------|
| 親エピック | `1214879360917675` |
| 親 URL | https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1214879360917675 |
| スモーク対象子（【1/12】） | `1214877045257081` |

## 使用 workflow

| 段階 | ファイル |
|------|----------|
| 企画 | `workflows/default.yaml` |
| 配賦 | `workflows/with-dispatch.yaml` → `task-dispatcher` |
| 開発課 | `workflows/development-delivery.yaml` → `product-manager` |

## 手順（ドライラン可）

```powershell
# 1. 子タスク内容
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\fetch_task.py --gid 1214877045257081

# 2. dispatch（エージェント）— DispatchRequest department=development
#    → product-manager prompt_snippet

# 3. PM workflow（エージェント）— 本スモークでは設計 doc 作成で done_when 相当を満たす

# 4. 完了マーク（実施済みエピック作業後）
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\complete_task.py --gid <CHILD_GID> -y
```

## ルーティング確認

| department | workflow_id | entry_agent | 状態 |
|------------|-------------|-------------|------|
| development | development-delivery | product-manager | 実装済み |
| analysis | analysis-delivery | analysis-lead | プレースホルダ（enabled: false） |

## 完了報告先

子完了: `DeptWorkComplete` → **workflow-orchestrator**（全子完了でエピック完了報告）。

## リポジトリ成果物（本実行）

- `docs/design/org-dispatch-model.md`
- `workflows/organizations.yaml`, `development-delivery.yaml`, `with-dispatch.yaml`
- `skills/task-dispatcher/`, `product-manager/`, `doc-writer/`, `developer/`, `reviewer/`
- Handoff v1.2 スキーマ・`asana_program_common` の `課:` 行
