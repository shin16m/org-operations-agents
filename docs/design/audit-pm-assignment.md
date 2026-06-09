# audit-pm 厳密運用 — 組織整合性監査

| 版 | 1.0 |
| 適用 | 監査チーム L3（`audit-delivery`） |

## 原則

1. **audit-pm は検証スクリプトを自分で実行して report を書かない**（→ consistency-auditor サブタスク）
2. **必須:** `pm_assign_subtasks.py` でサブ 2 件（auditor → reviewer）
3. ワーカー完了ごとに PM が当該サブを complete → 全サブ完了後に親 comment → complete → `DeptWorkComplete`

## 必須フロー

```
1. fetch_task.py --gid <子GID> --show-assignee
2. pm_assign_subtasks.py --plan skills/audit/examples/assign-plan.org-governance-v1.json --department audit --update-parent-assignee audit-pm -y
3. **デフォルト:** **check_pm_review_gate.py** exit 0（gate 無し）→ L3b  
   **opt-in**（`human_review_gate: true` / `--require-human-review` / `ORG_OPS_PM_REVIEW_GATE=1`）: **create_pm_review_gate.py** → 人間 complete → check exit 0
4. L3b: consistency-auditor セッションへ WorkerDispatchSnippet
5. auditor 完了後 audit-reviewer セッションへ
6. 全サブ完了 → 親 comment_task → complete_task → DeptWorkComplete
```

## PM が書いてはいけない成果物

| パス | 担当 |
|------|------|
| `output/audit/reports/` | consistency-auditor |
| `output/audit/reviews/` | audit-reviewer |

**comment_task:** PM slug で auditor / reviewer の作業を署名しない。実装作業は各ワーカー slug。

プラン例: [`assign-plan.org-governance-v1.json`](../../skills/audit/examples/assign-plan.org-governance-v1.json)

マイルストーン tracker 監査: [`assign-plan.milestone-tracker-audit-v1.json`](../../skills/audit/examples/assign-plan.milestone-tracker-audit-v1.json)

## 参照

- [`audit-delivery-io.md`](audit-delivery-io.md)
- L3b: [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md)
- レビュー NG: [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)
