# task-dispatcher

Asana **子タスク 1 件**を、課（開発課・分析課など）の workflow 入口へルーティングするスキルです。

## いつ使うか

- `asana-buddy` でエピック作成済み
- オーケストレーターから「子タスク GID ○○ を実行」＝配賦依頼

## 手順

1. `DispatchRequest`（`task_gid`, `department`）を受け取る
2. [`workflows/organizations.yaml`](../../../workflows/organizations.yaml) で `workflow_id` / `entry_agent` を解決
3. 課の entry（例: `product-manager`）用 **prompt_snippet** を返す

## 参照

- [`SKILL.md`](SKILL.md)
- [`docs/design/org-dispatch-model.md`](../../../docs/design/org-dispatch-model.md)
