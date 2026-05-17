# task-dispatcher SKILL

**独立スキル:** 子タスク 1 件を **課** に振り分ける（L2 配賦）。課内作業はしない。

人間向け: [`README.md`](README.md) · I/O: [`docs/design/dept-work-io.md`](../../docs/design/dept-work-io.md)

## 入力

`DispatchRequest` v1.0（[`schemas/dispatch-request.v1.schema.json`](schemas/dispatch-request.v1.schema.json)）

- `task_gid`（必須）
- `department`（必須）: `development` | `analysis` | `planning`
- `parent_gid`（任意）

`department` 未指定時: `fetch_task.py` で notes を読み、`課:` 行または `pillar_defaults` で推定。

## 出力

- 解決した `workflow_id` と `entry_agent`
- **entry_agent 用 prompt_snippet**（1 ブロック）

`prompt_snippet` には、課内作業完了時に **`complete_task.py -y` を `DeptWorkComplete` の前に実行する**旨を 1 行含める（[`docs/design/dept-work-io.md`](../../docs/design/dept-work-io.md)）。

## ルーティング

[`workflows/organizations.yaml`](../../workflows/organizations.yaml) を読む。

| department | workflow | entry |
|------------|----------|-------|
| development | development-delivery | product-manager |
| analysis | analysis-delivery | analysis-lead（未実装時は blocked） |
| planning | — | dispatch 対象外（L1 で完結） |

## やらないこと

- Handoff 新規作成
- 要件定義・コーディング・レビュー本体
- Asana 親+子の一括作成（→ asana-buddy）
- `skills/<slug>/` 新規生成（→ agent-creater）

## 起動例

```
DispatchRequest: task_gid=1214877045257081, department=development, parent_gid=1214879360917675
organizations.yaml に従い product-manager 用 prompt_snippet を返してください。
```
