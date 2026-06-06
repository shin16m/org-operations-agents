# org-os watch Task Type フィルタ — delivery 記録

| 項目 | 内容 |
|------|------|
| エピック | `1215089212767842` |
| development 子 | `1215089213220698` |
| governance 子 | `1215089213185363` |
| audit 子 | `1215089030440977` |
| 日付 | 2026-05-24 |

## 【2/4】development

- `tools/sync_task_type_env.py`
- `asana_program_common.set_task_type_epic`
- `org-os watch` — Agent Type=AI + Task Type=Epic フィルタ
- `handoff_to_asana` epic create 時 Task Type=Epic

## 【3/4】governance

- `docs/design/asana-task-type-field.md` v1.0
- `workflow-orchestrator/SKILL.md` 起票ルール
- `org-os-product-io.md` watch 条件

## 検証

```
WATCH  project=1214771428861230  ready=1  waiting=0  skipped=108  filter=AgentType:AI+TaskType:Epic
```
