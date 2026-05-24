# PM 委譲品質ゲート（assign review gate）— 運用 SSOT

| 版 | 1.0 |
| 日付 | 2026-05-24 |
| エピック | `1215086194042850` |

## 目的

L3 PM が `pm_assign_subtasks` でサブを作成した**後**、**L3b worker dispatch 前**に人間がサブ構成・担当割り当てをレビューする。

## フロー（L3 チーム内）

```
PM: pm_intake → pm_assign_subtasks
  → create_pm_review_gate.py（承認サブ「【レビュー】サブ構成・担当割り当て」）
  → 人間が承認サブを complete
  → check_pm_review_gate.py exit 0
  → L3b: pm_emit_worker_prompt / WorkerDispatchSnippet
  → ワーカー各サブ complete …
```

## 承認 = 完了

- **完了** = サブ構成 OK → worker dispatch 可
- **未完了 + 親コメント** = 差し戻し → PM が assign plan 再作成 → **新レビューサブ**（`【レビュー】` プレフィックス）

## 禁止（pm-review-rework SSOT 整合）

- 完了済み承認サブの `complete_task --undo` で再開
- PM slug でワーカー作業を `comment_task`
- 承認サブなしで L3b dispatch

## CLI

```powershell
# assign plan 作成後
python tools/create_pm_review_gate.py --parent <PM子GID> --plan work/assign-plans/<plan>.json -y

# dispatch 前（人間 complete 後）
python tools/check_pm_review_gate.py --parent <PM子GID>
```

共通 helper: [`create_approval_subtask.py`](../../skills/platform/asana-buddy/optional/create_approval_subtask.py) · [`check_approval_subtask.py`](../../skills/platform/asana-buddy/optional/check_approval_subtask.py)

## PM assignment doc への追記

全 PM 厳密運用 doc（development / ux / analytics / governance / audit）に本 gate を **pm_assign 直後**の必須手順として記載。

## 参照

- [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)
- [`planning-governance-brushup.md`](planning-governance-brushup.md)
