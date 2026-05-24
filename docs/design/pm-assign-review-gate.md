# PM 委譲品質ゲート（assign review gate）— 運用 SSOT

| 版 | 1.2 |
| 日付 | 2026-05-24 |
| エピック | `1215086341081688` · F1/F3 |

## 目的

L3 PM が `pm_assign_subtasks` でサブを作成した**後**、**L3b worker dispatch 前**に人間がサブ構成・担当割り当てをレビューする。

**サブ作成前の人間承認は不要。** 利用者が確認したいのは **作成済みサブの一覧と担当 slug** である。

## フロー（L3 チーム内）

```
PM: pm_intake → pm_assign_subtasks（サブ作成 · 担当 notes · worker CF 試行）
  → create_pm_review_gate.py（承認サブ「【レビュー】サブ構成・担当割り当て」+ worker→gate dependencies）
  → 【停止】人間が Asana 上で承認サブを complete（エージェントは complete しない）
  → check_pm_review_gate.py exit 0
  → L3b: pm_emit_worker_prompt / WorkerDispatchSnippet
  → ワーカー各サブ …
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
# assign plan 作成後
python tools/create_pm_review_gate.py --parent <PM子GID> --plan work/assign-plans/<plan>.json -y

# dispatch 前（人間が Asana UI で complete した後のみ）
python tools/check_pm_review_gate.py --parent <PM子GID>
```

共通 helper: [`create_approval_subtask.py`](../../skills/platform/asana-buddy/optional/create_approval_subtask.py) · [`check_approval_subtask.py`](../../skills/platform/asana-buddy/optional/check_approval_subtask.py) · [`asana_program_common.py`](../../skills/platform/asana-buddy/optional/asana_program_common.py)（`add_task_dependencies` / `wire_worker_subs_to_review_gate`）

承認サブ作成時: 担当種別 CF = **human**（担当=人間 · org-ops 自動設定。「手動設定のみ」ではない — [`asana-assignee-type-field.md`](asana-assignee-type-field.md) v1.5）

## planning gate との違い

[`planning-gate-vs-pm-review-gate.md`](planning-gate-vs-pm-review-gate.md)

## PM assignment doc への追記

全 PM 厳密運用 doc（development / ux / analytics / governance / audit）に本 gate を **pm_assign 直後**の必須手順として記載。

## 参照

- [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)
