# intake 元 Asana タスククローズ — dryrun 記録

| エピック | `1215085684107323` |
| development 子 | `1215085905698627` |
| intake 元 | `1215082835252589` |
| ソース | `1215082835252589` |

## 手順

### 1. bootstrap 後 — 元タスクをクローズ

```powershell
$env:PYTHONIOENCODING="utf-8"
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\close_intake_source_task.py `
  --source 1215082835252589 --epic 1215085684107323 -y
```

### 2. 相互リンク確認

| タスク | 期待 |
|--------|------|
| 元 `1215082835252589` | 署名コメントに新エピック URL · **completed** |
| 新エピック `1215085684107323` | notes 先頭 `## ソース Asana タスク` に元 URL/GID |

## 実装

- `close_intake_source_task.py` — comment + complete
- `workflow-orchestrator/SKILL.md` — bootstrap 直後 step
- `docs/design/workflow-session-io.md` — `close_intake_source` · `source_task_closed`

## 参照

- intake-asana dryrun: [`asana-task-intake-dryrun.md`](asana-task-intake-dryrun.md)
