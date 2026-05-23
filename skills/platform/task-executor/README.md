# task-executor

Asana に載った**サブタスクを実行**するスキルです（計画・タスク化の後段）。

## いつ使うか

- `asana-buddy` でエピック／サブタスクを作成した**あと**
- 「Asana の ○○ 番タスクを実行して」と自然言語で依頼するとき

**プロンプトでスキル名を指定する必要はありません**（エージェントが workflow に従って起動します）。

## 手順（要約）

1. 対象タスク GID を決める（Asana URL または親の subtasks 一覧）
2. タスク内容を取得:

   ```powershell
   .\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <TASK_GID>
   ```

3. 本スキル（task-executor）で `notes` の完了条件まで作業
4. 完了マーク（**エージェントが `done_when` 達成と判断したら `-y` で実行してよい**）:

   ```powershell
   .\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\complete_task.py --gid <TASK_GID> -y
   ```

`--json` 出力は Windows コンソールで文字化けしやすいため、ファイルへリダイレクトすること。

本スキルは agent-creater 契約に沿った手動整備（テンプレ生成物）です。

## workflow

拡張 workflow: [`workflows/with-execution.yaml`](../../../workflows/with-execution.yaml)（execute の次が `work`）。

## 参照

- [`SKILL.md`](SKILL.md)
- [`docs/design/task-execution-boundary.md`](../../../docs/design/task-execution-boundary.md)
