# タスク実行フェーズ スモーク

エピック: タスク実行フェーズ・Asana 着手エージェント（Handoff: `handoff.task-executor-agent.json`）

## 実施

2026-05-17 — エピック全サブタスク（1–7）をリポジトリ上で実装。

## 確認項目

| 項目 | 結果 |
|------|------|
| `docs/design/task-execution-boundary.md` | 作成済み |
| `docs/design/task-work-io.md` | 作成済み |
| `skills/platform/task-executor/` | README / SKILL / personas |
| `fetch_task.py` / `complete_task.py` | 追加済み |
| `workflows/with-execution.yaml` | 新設 |
| `agent-registry.yaml` | task-executor 登録 |

## 手順（再現）

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid 1214879353098996 --list-subtasks
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <CHILD_GID>
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\complete_task.py --gid <CHILD_GID> -y
```

## Asana

- 親: https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1214879353098996
