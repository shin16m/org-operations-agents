# task-dispatcher SKILL

**独立スキル:** 子タスク 1 件を **チーム** に振り分ける（L2 配賦）。チーム内作業はしない。

人間向け: [`README.md`](README.md) · I/O: [`docs/design/dept-work-io.md`](../../../docs/design/dept-work-io.md) · **prompt SSOT:** [`docs/design/dispatch-prompt-ssot.md`](../../../docs/design/dispatch-prompt-ssot.md)

## 入力

`DispatchRequest` v1.0（[`schemas/dispatch-request.v1.schema.json`](schemas/dispatch-request.v1.schema.json)）

- `task_gid`（必須）
- `department`（必須）: `development` | `analysis` | `planning` | `ux` | `governance` | `audit`
- `parent_gid`（任意）

`department` 未指定時: `fetch_task.py` で notes を読み、`チーム:` 行または `pillar_defaults` で推定。

## 出力

- 解決した `workflow_id` と `entry_agent`
- **entry_agent 用 prompt_snippet**（1 ブロック）

### prompt_snippet 生成（必須）

1. [`docs/design/dispatch-prompt-ssot.md`](../../../docs/design/dispatch-prompt-ssot.md) の **該当 department 節**を開く
2. `{task_gid}` / `{parent_gid}` を置換
3. **省略・要約・「workflow を全部実行」への書き換えをしない**
4. ux / development / analysis / audit では **intake 最初の 1 手 = pm_assign_subtasks** を必ず含める（audit は 2 サブ固定プラン可）

`prompt_snippet` には、チーム PM 完了時に **`comment_task.py`（署名付き）→ `complete_task.py -y` → `DeptWorkComplete`** の順も含める（[`dept-work-io.md`](../../../docs/design/dept-work-io.md)）。

## ルーティング

[`workflows/organizations.yaml`](../../../workflows/organizations.yaml) を読む。

| department | workflow | entry | assignment SSOT |
|------------|----------|-------|-----------------|
| planning | planning-delivery | planning-pm | [`planning-delivery-io.md`](../../../docs/design/planning-delivery-io.md) |
| development | development-delivery | product-manager | [`development-pm-assignment.md`](../../../docs/design/development-pm-assignment.md) |
| analysis | analysis-delivery | analytics-pm | [`analytics-pm-assignment.md`](../../../docs/design/analytics-pm-assignment.md) |
| ux | ux-delivery | ux-pm | [`ux-pm-assignment.md`](../../../docs/design/ux-pm-assignment.md) |
| governance | governance-delivery | governance-pm | [`governance-pm-assignment.md`](../../../docs/design/governance-pm-assignment.md) |
| audit | audit-delivery | audit-pm | [`audit-pm-assignment.md`](../../../docs/design/audit-pm-assignment.md) |

## 配賦順序（推奨）

1. **L1 初回:** intake 後の bootstrap 企画子 → `department=planning`
2. **L2 続き:** 企画完了後 → **`ux`（Web Epic・UI 先行）** → `development` / `analysis` → **`governance`（org-meta）** → **`audit`（組織変更時・最後）**

## やらないこと

- Handoff 新規作成（→ issue-story-planner / planning-pm）
- 要件定義・コーディング・レビュー本体
- PM の代わりに worker 成果物を書く指示
- dispatch-prompt-ssot を飛ばした独自 prompt（SSOT 逸脱）

## 起動例

```
DispatchRequest: task_gid=1214877045257081, department=development, parent_gid=1214879360917675
organizations.yaml に従い、dispatch-prompt-ssot.md の development 節から product-manager 用 prompt_snippet を返してください。
```
