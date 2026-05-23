# task-dispatcher

Asana **子タスク 1 件**を、チーム（企画 / UX / 開発 / 分析）の workflow 入口へルーティングするスキルです。

## いつ使うか

- bootstrap 後（初回 = 企画子 `department=planning`）
- 企画完了後（execution 系子 `ux` → `development` / `analysis`）
- オーケストレーターから「子タスク GID ○○ を実行」＝配賦依頼

## 手順

1. `DispatchRequest`（`task_gid`, `department`）を受け取る
2. [`workflows/organizations.yaml`](../../../workflows/organizations.yaml) で `workflow_id` / `entry_agent` を解決
3. [`docs/design/dispatch-prompt-ssot.md`](../../../docs/design/dispatch-prompt-ssot.md) の該当節から **prompt_snippet** を組み立てて返す（独自要約禁止）

## ルーティング

| department | entry |
|------------|-------|
| planning | planning-pm |
| ux | ux-pm |
| development | product-manager |
| analysis | analytics-pm |

## 参照

- [`SKILL.md`](SKILL.md)
- [`docs/design/dispatch-prompt-ssot.md`](../../../docs/design/dispatch-prompt-ssot.md)
- [`docs/design/org-dispatch-model.md`](../../../docs/design/org-dispatch-model.md)
