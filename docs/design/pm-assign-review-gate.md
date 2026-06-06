# PM 委譲品質ゲート（assign review gate）— 運用 SSOT

| 版 | 1.3 |
| 日付 | 2026-06-05 |
| エピック | `1215086341081688` · F1/F3 · **`1215465361526049`**（opt-in 化） |

## 目的

L3 PM が `pm_assign_subtasks` 後、**必要なときだけ**人間がサブ構成・担当割り当てをレビューする（**エージェント評価・監査用 opt-in**）。

**通常運用（デフォルト）:** assign 後 **すぐ L3b**（【レビュー】サブ構成・担当割り当て **を作らない**）。

## フロー（L3 チーム内）

### デフォルト（通常）

```
PM: pm_intake → pm_assign_subtasks
  → create_pm_review_gate.py（no-op · SKIP）
  → check_pm_review_gate.py exit 0（gate 無し）
  → L3b: pm_emit_worker_prompt
```

### opt-in（評価・監査）

トリガー（いずれか）:

- assign plan `"human_review_gate": true`
- `create_pm_review_gate.py --require-human-review`
- env `ORG_OPS_PM_REVIEW_GATE=1`
- PM 子 notes `human_review_gate: yes`

```
PM: pm_assign_subtasks
  → create_pm_review_gate.py（【レビュー】サブ構成・担当割り当て + dependencies）
  → 人間 complete（エージェント禁止）
  → check_pm_review_gate.py exit 0
  → L3b
```

## Asana dependencies（F1）

`create_pm_review_gate.py` は gate 作成後、`wire_worker_subs_to_review_gate` で **各 worker サブ → 【レビュー】サブ** の dependency を設定する。

- API: `POST /tasks/{worker_gid}/addDependencies`
- 【レビュー】/【承認】サブ自身には dependency を付けない
- `pm_emit_worker_prompt` は `check_pm_review_gate` exit 0 前は **exit 1**

## 承認 = 人間による Asana complete

- **完了** = サブ構成 OK → worker dispatch 可
- **未完了** = L3b dispatch **禁止**（「すすめて」等のチャット指示でエージェントが代行 complete しない）
- **差し戻し** = 未完了のまま親にコメント → PM が assign plan 再作成 → **新レビューサブ**（`【レビュー】` プレフィックス）

## 禁止

| 禁止 | 理由 |
|------|------|
| サブ作成**前**に人間承認を求める | F1 フィードバック。assign 後 review が正 |
| エージェントが `complete_task.py` で【レビュー】/【承認】サブを complete | F3。`complete_task` は exit 3 で拒否 |
| 完了済み承認サブの `complete_task --undo` で再開 | 監査履歴 |
| PM slug でワーカー作業を `comment_task` | worker dispatch SSOT |
| `check_pm_review_gate` exit 0 前の L3b dispatch | gate 未達 |

## CLI

```powershell
# assign plan 作成後（opt-in 時のみ gate 作成）
python tools/create_pm_review_gate.py --parent <PM子GID> --plan work/assign-plans/<plan>.json -y
python tools/create_pm_review_gate.py --parent <PM子GID> --plan <plan>.json --require-human-review -y

# dispatch 前（gate 無し → exit 0 / gate pending → exit 1）
python tools/check_pm_review_gate.py --parent <PM子GID>
```

共通 helper: [`create_approval_subtask.py`](../../skills/platform/asana-buddy/optional/create_approval_subtask.py) · [`check_approval_subtask.py`](../../skills/platform/asana-buddy/optional/check_approval_subtask.py) · [`asana_program_common.py`](../../skills/platform/asana-buddy/optional/asana_program_common.py)（`add_task_dependencies` / `wire_worker_subs_to_review_gate`）

承認サブ作成時: Agent Type CF = **human**（担当=人間 · org-ops 自動設定。「手動設定のみ」ではない — [`asana-assignee-type-field.md`](asana-assignee-type-field.md) v1.6）

## planning gate との違い

[`planning-gate-vs-pm-review-gate.md`](planning-gate-vs-pm-review-gate.md)

## PM assignment doc への追記

全 PM 厳密運用 doc（development / ux / analytics / governance / audit）に本 gate を **pm_assign 直後**の必須手順として記載。

## 参照

- [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)
