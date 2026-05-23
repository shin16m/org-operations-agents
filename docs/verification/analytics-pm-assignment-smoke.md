# Smoke — analytics-pm 厳密アサイン

| 前提 | `.env` に `ASANA_TOKEN`, `ASANA_PROJECT_ID` |
| エピック | `1215080188661796` |

## 1. 担当ヘッダの更新

```powershell
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\update_task_notes.py `
  --gid 1215079357115371 --assignee analytics-pm --status in_progress --preserve-body -y
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid 1215079357115371 --show-assignee
```

期待: `担当: analytics-pm`

## 2. チーム内サブタスク作成

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent 1215079357115371 --plan .\work\assign-plans\fishing-task-1-strict.json -y
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid 1215079357115371 --list-subtasks
```

期待: 【1/7-1】担当 data-architect、【1/7-2】担当 analysis-reviewer

## 3. レビュー NG（修正タスク）

PM 差し戻しは **修正サブタスクの新規追加**。`--undo` は使わない。

参照: [`pm-review-rework-ssot.md`](../design/pm-review-rework-ssot.md)

## 参照

- [`analytics-pm-assignment.md`](../design/analytics-pm-assignment.md)
