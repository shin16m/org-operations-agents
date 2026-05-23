# Smoke — product-manager 厳密アサイン

| 前提 | `.env` に `ASANA_TOKEN`, `ASANA_PROJECT_ID` |
| 対象 | development 子タスク GID（Epic 内・`department=development`） |

## 1. 親タスクの profile / 担当

```powershell
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\update_task_notes.py `
  --gid <PARENT_GID> --department development --assignee product-manager --status in_progress --preserve-body -y
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <PARENT_GID> --show-assignee
```

期待: `チーム: development` · `担当: product-manager`

## 2. チーム内サブタスク作成（lite 例）

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent <PARENT_GID> --plan .\skills\development\examples\assign-plan.lite-v1.json `
  --department development --update-parent-assignee product-manager -y
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <PARENT_GID> --list-subtasks
```

期待: 各サブに `担当: requirements-writer` / `dev-reviewer` / `developer` 等が設定されている。

## 3. ワーカー着手前確認

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <SUB_GID> --show-assignee
```

期待: 起動するエージェント slug と `担当:` が一致。

## 4. レビュー NG（修正タスク）

```powershell
python tools/pm_create_fix_subtask.py --parent <PARENT_GID> --review-json skills/development/examples/review-result.code-failed.example.json --dry-run
```

参照: [`pm-review-rework-ssot.md`](../design/pm-review-rework-ssot.md)

## 参照

- [`development-pm-assignment.md`](../design/development-pm-assignment.md)
- [`assign-plan.lite-v1.json`](../../skills/development/examples/assign-plan.lite-v1.json)
