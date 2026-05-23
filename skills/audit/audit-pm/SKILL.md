# audit-pm SKILL

**独立スキル:** 監査チームにおける **子タスク 1 件**の進行管理（L3 ハブ）。

人間向け: [`README.md`](README.md) · workflow: [`workflows/audit-delivery.yaml`](../../../workflows/audit-delivery.yaml) · **厳密アサイン:** [`docs/design/audit-pm-assignment.md`](../../../docs/design/audit-pm-assignment.md) · **dispatch 起動:** [`docs/design/dispatch-prompt-ssot.md`](../../../docs/design/dispatch-prompt-ssot.md#audit)

## 厳密運用（必須）

1. **自分で validate スクリプトを実行して report を書かない**（→ consistency-auditor サブタスク）。
2. 子タスクを分析し、**担当エージェント**を決める → **Asana サブタスク**を作成（`pm_assign_subtasks.py` 必須）。
3. 担当エージェントが `fetch_task.py --show-assignee` で自分の slug と一致することを確認してから実行。
4. 委譲先が **comment_task** → PM が子サブタスクを **complete** → 全サブ完了後に親を **comment → complete**。

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent <親GID> --plan .\skills\audit\examples\assign-plan.org-governance-v1.json `
  --department audit --update-parent-assignee audit-pm -y
```

再実施・差し戻し: **`complete_task --undo` 禁止**。review `failed` → `python tools/pm_create_fix_subtask.py --parent <子GID> --review-json output/audit/reviews/<file>.json [--fix-assignee consistency-auditor] -y`（[`pm-review-rework-ssot.md`](../../../docs/design/pm-review-rework-ssot.md)）

## ワーカー dispatch（L3b・必須）

`pm_assign_subtasks` 後、consistency-auditor / audit-reviewer は **別セッション**で起動する。

```powershell
python tools/pm_emit_worker_prompt.py --parent <親GID> --department audit
```

PM セッションは snippet 出力後一旦終了。SSOT: [`pm-worker-dispatch-ssot.md`](../../../docs/design/pm-worker-dispatch-ssot.md)

## 責務

1. `fetch_task.py --gid <task_gid> --show-assignee` で子の notes を読む
2. 親エピック notes を文脈として参照（監査対象・変更概要）
3. [`audit-delivery.yaml`](../../../workflows/audit-delivery.yaml) に沿い委譲:
   - **consistency-auditor** — 機械検証 + `ConsistencyAuditReport`
   - **audit-reviewer** — `AuditReviewResult`（`review_kind: org_governance`）
4. review `failed` → **修正サブ**を新規作成 → 再 review サブ
5. 子の `done_when` を満たしたら **comment_task → complete_task -y → DeptWorkComplete**
6. **workflow-orchestrator** へ完了報告

## Asana 記録（必須・順序）

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py --gid <子GID> --agent audit-pm --skill skills/audit/audit-pm/SKILL.md --summary "監査子タスク完了" --body "..." -y
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\complete_task.py --gid <子GID> -y
```

契約: [`docs/design/agent-asana-comment-signature.md`](../../../docs/design/agent-asana-comment-signature.md) · 運用: [`docs/design/audit-delivery-io.md`](../../../docs/design/audit-delivery-io.md)

## 出力

完了時: `DeptWorkComplete`（`department: audit`）— [`schemas/dept-work-complete.v1.schema.json`](../../development/product-manager/schemas/dept-work-complete.v1.schema.json)

## やらないこと

- validate スクリプトの実行・report JSON の直接作成（→ consistency-auditor）
- registry / workflow の **修正実装**（findings のみ。修正は開発子へ）
- Handoff 新規作成（→ 企画チーム）
- dispatch（→ task-dispatcher）
