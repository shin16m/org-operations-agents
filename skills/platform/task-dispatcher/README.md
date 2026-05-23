# task-dispatcher

Asana **子タスク 1 件**を、チーム（企画チーム・開発チーム・分析チーム）の workflow 入口へルーティングするスキルです。

## いつ使うか

- bootstrap 後（初回 = 企画子 `department=planning`）
- 企画完了後（execution 系子 `department=development` / `analysis`）
- オーケストレーターから「子タスク GID ○○ を実行」＝配賦依頼

## 手順

1. `DispatchRequest`（`task_gid`, `department`）を受け取る
2. [`workflows/organizations.yaml`](../../../workflows/organizations.yaml) で `workflow_id` / `entry_agent` を解決
3. チームの entry（例: `planning-pm`, `product-manager`）用 **prompt_snippet** を返す

## ルーティング

| department | entry |
|------------|-------|
| planning | planning-pm |
| development | product-manager |
| analysis | analytics-pm |

## 参照

- [`SKILL.md`](SKILL.md)
- [`docs/design/org-dispatch-model.md`](../../../docs/design/org-dispatch-model.md)
