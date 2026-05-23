# work/ — 実行時ワークスペース

本リポジトリは **組織テンプレート** です。`work/` は fork 先・ローカル実行時に PM が使う作業領域（git 管理対象外のファイルを置く）。

## assign-plans/

**PM が L3b で Asana サブタスクを切る前の assign plan JSON** を置く。

| 項目 | 内容 |
|------|------|
| 用途 | `pm_assign_subtasks.py --plan work/assign-plans/<plan>.json ...` の入力 |
| 形式 | [`skills/*/examples/assign-plan*.json`](../skills/development/examples/assign-plan.full-ui-v1.json) と同じ schema |
| git | **フォルダのみテンプレ**。`*.json` はコミットしない（エピック固有の実行記録） |

### フロー（analytics-pm / ux-pm / product-manager 共通）

1. `fetch_task.py --gid <親GID> --show-assignee`
2. 完了条件から作業単位を分解
3. assign plan JSON を `work/assign-plans/<epic>-<dept>.json` に保存
4. `pm_assign_subtasks.py --parent <GID> --plan work/assign-plans/<plan>.json --department <dept> --update-parent-assignee <pm-slug> -y`

**雛形（git 管理）:** `skills/development/examples/`, `skills/ux/examples/`, `skills/analysis/examples/` の `assign-plan*.json`

参照: [`docs/design/analytics-pm-assignment.md`](../docs/design/analytics-pm-assignment.md) · [`docs/design/dispatch-prompt-ssot.md`](../docs/design/dispatch-prompt-ssot.md)

---

## 成果物（チーム deliverable）

要件・コード・レビュー JSON 等は **`output/<department>/`** へ（[`output/README.md`](../output/README.md)）。こちらも実行時ファイルは原則 git 管理外。
