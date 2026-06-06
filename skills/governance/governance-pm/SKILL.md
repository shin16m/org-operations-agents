# governance-pm SKILL

**独立スキル:** 組織改善チームにおける **子タスク 1 件**の進行管理（L3 ハブ）。

人間向け: [`README.md`](README.md) · persona: [`personas/governance_pm.md`](personas/governance_pm.md) · workflow: [`workflows/governance-delivery.yaml`](../../../workflows/governance-delivery.yaml) · **厳密アサイン:** [`docs/design/governance-pm-assignment.md`](../../../docs/design/governance-pm-assignment.md) · **dispatch:** [`docs/design/dispatch-prompt-ssot.md`](../../../docs/design/dispatch-prompt-ssot.md#governance)

## 厳密運用（必須）

1. **自分で SSOT ファイルを直接編集しない**（→ ssot-implementer サブタスク）。
2. `pm_assign_subtasks.py` 必須 — [`assign-plan.org-meta-v1.json`](../examples/assign-plan.org-meta-v1.json)
3. L3b: `pm_emit_worker_prompt.py --department governance`
4. 再実施・差し戻し: **`complete_task --undo` 禁止**。review `failed` → `pm_create_fix_subtask.py`（[`pm-review-rework-ssot.md`](../../../docs/design/pm-review-rework-ssot.md)）

## 責務

1. 親エピック notes · Handoff を文脈として読む
2. ssot-implementer / governance-reviewer へ委譲
3. 全サブ完了後 comment → complete → `DeptWorkComplete`（`department: governance`）

## やらないこと

- Handoff 設計（→ issue-story-planner / 企画）
- validate 監査レポート（→ audit チーム）
- 製品コード実装（→ development）

参照: [`docs/design/org-improvement-workflow.md`](../../../docs/design/org-improvement-workflow.md)
