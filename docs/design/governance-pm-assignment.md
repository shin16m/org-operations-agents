# governance-pm — サブタスク分解（厳密運用）

| 版 | 1.0 |
| 日付 | 2026-05-24 |

## 必須手順

1. `fetch_task.py --gid <子GID> --show-assignee`
2. 親エピック notes · Handoff governance 子の done_when を確認
3. `pm_assign_subtasks.py` — **必須**

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent <親GID> --plan .\skills\governance\examples\assign-plan.org-meta-v1.json `
  --department governance --update-parent-assignee governance-pm -y
```

5. **create_pm_review_gate.py** → 人間 complete → **check_pm_review_gate.py exit 0**
6. `python tools/pm_emit_worker_prompt.py --parent <子GID> --department governance`
7. サブ完了ごとに complete → 親 comment → 親 complete → `DeptWorkComplete`

## 禁止

- PM が ssot-implementer の役割で registry/doc を直接編集
- PM が GovernanceReviewResult を自己作成
- サブ未作成で `担当:` だけワーカー slug に変更
- **PM slug で ssot-implementer / governance-reviewer の作業を comment_task する**

## review NG

`governance-reviewer` failed → `pm_create_fix_subtask.py`（[`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)）

プラン例: [`assign-plan.org-meta-v1.json`](../../skills/governance/examples/assign-plan.org-meta-v1.json)
