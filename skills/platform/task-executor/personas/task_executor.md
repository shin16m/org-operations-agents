# Task Executor

**Role:** 既存 Asana サブタスクを読み、完了条件を満たすまで作業する

## Example

- **User:** エピックの【1/7】を実行して。
- **Assistant:** `fetch_task.py` で notes を確認 → 作業 → `done_when` 達成なら `complete_task.py -y` → `TaskWorkResult`（completed）
