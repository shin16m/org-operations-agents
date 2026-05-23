# task-dispatcher SKILL

**独立スキル:** 子タスク 1 件を **チーム** に振り分ける（L2 配賦）。チーム内作業はしない。

人間向け: [`README.md`](README.md) · I/O: [`docs/design/dept-work-io.md`](../../../docs/design/dept-work-io.md)

## 入力

`DispatchRequest` v1.0（[`schemas/dispatch-request.v1.schema.json`](schemas/dispatch-request.v1.schema.json)）

- `task_gid`（必須）
- `department`（必須）: `development` | `analysis` | `planning`
- `parent_gid`（任意）

`department` 未指定時: `fetch_task.py` で notes を読み、`チーム:` 行または `pillar_defaults` で推定。

## 出力

- 解決した `workflow_id` と `entry_agent`
- **entry_agent 用 prompt_snippet**（1 ブロック）

`prompt_snippet` には、チーム内作業完了時に **`comment_task.py`（署名付き）→ `complete_task.py -y` → `DeptWorkComplete`** の順を含める（[`docs/design/dept-work-io.md`](../../../docs/design/dept-work-io.md) · [`agent-asana-comment-signature.md`](../../../docs/design/agent-asana-comment-signature.md)）。

## ルーティング

[`workflows/organizations.yaml`](../../../workflows/organizations.yaml) を読む。

| department | workflow | entry |
|------------|----------|-------|
| planning | planning-delivery | planning-pm |
| development | development-delivery | product-manager |
| analysis | analysis-delivery | analytics-pm |

## 配賦順序（推奨）

1. **L1 初回:** intake 後の bootstrap 企画子 → `department=planning`
2. **L2 続き:** 企画完了（Handoff Asana 投入）後 → `development` / `analysis` の execution 系子

## やらないこと

- Handoff 新規作成（→ issue-story-planner / planning-pm）
- 要件定義・コーディング・レビュー本体
- 企画 gate（→ planning-pm）
- 新規 `skills/<organization>/<slug>/`（→ agent-creater）

## 起動例

```
DispatchRequest: task_gid=1214877045257081, department=planning, parent_gid=1214879360917675
organizations.yaml に従い planning-pm 用 prompt_snippet を返してください。
```
