# analytics-pm 厳密運用 — チーム内アサインと Asana 記録

| 版 | 1.1 |
| 日付 | 2026-05-23 |
| 適用 | 分析チーム L3（`analysis-delivery`） |

## 原則

1. **analytics-pm は自分で実装しない**（要求定義・進行・完了集約を除く）。
2. PM が dispatch された子タスクを読み、**作業単位を洗い出す**。
3. **必須:** 洗い出したタスクを **Asana サブタスク** に分解し、各 notes に **担当 slug** を書く（単一タスクに PM 以外を直接委譲しない）。
4. **担当エージェントだけ**がそのサブタスクを実行する（notes の `担当:` と自分の slug が一致すること）。
5. 完了は **担当の comment_task → PM が当該サブを complete → 全サブ完了後に親を comment → complete**。

**comment_task:** PM slug で data-* / analysis-reviewer の作業を署名しない。実装作業は notes `担当:` のワーカー slug。

**dispatch 起動文 SSOT:** [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md#analysis)

## PM の必須フロー（intake）

```
1. fetch_task.py --gid <親子GID> --show-assignee
2. 完了条件から作業単位を分解
3. assign plan JSON を work/assign-plans/ に残す
4. pm_assign_subtasks.py --department analysis --update-parent-assignee analytics-pm -y
5. **create_pm_review_gate.py** → 人間 complete → **check_pm_review_gate.py exit 0**
6. 親 notes → 担当: analytics-pm, 状態: in_progress
7. サブ完了のたびに PM が complete → 全サブ完了後 DeptWorkComplete
```

**禁止:** サブタスクを作らず、親 notes の `担当:` だけ data-engineer 等に書き換えて委譲すること。

## notes ヘッダ（必須・先頭）

```markdown
チーム: analysis

担当: data-engineer
状態: assigned

```

| フィールド | 値 |
|------------|-----|
| `チーム` | `analysis`（開発は `development`） |
| `担当` | [`agent-registry.yaml`](../../workflows/agent-registry.yaml) の `slug` |
| `状態` | `assigned` \| `in_progress` \| `review` \| `done` |

その下に Handoff 由来の `## 背景` / `## 概要` / `## 完了条件` を置く。

## サブタスク分解（例）

親: `【1/7・分析】…` — **担当: analytics-pm**（進行のみ）

| サブ | 担当 | 成果物 |
|------|------|--------|
| 【1/7-1】データソース設計 | data-architect | `output/analysis/strict-v2/data-source-design.md` |
| 【1/7-2】設計レビュー | analysis-reviewer | `output/analysis/strict-v2/reviews/...` |

## CLI

```powershell
# notes 更新（担当追記）
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\update_task_notes.py `
  --gid <GID> --assignee data-architect --status assigned --preserve-body -y

# チーム内サブタスク一括作成（JSON プラン）
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent <親GID> --plan .\work\assign-plans\<plan>.json `
  --department analysis --update-parent-assignee analytics-pm -y

# 担当確認
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <GID> --show-assignee
```

## L3b — ワーカー dispatch（必須）

サブ作成後、data-* / analysis-reviewer は **別セッション**で起動する。

```powershell
python tools/pm_emit_worker_prompt.py --parent <親GID> --department analysis
```

SSOT: [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md) — skill パスは **registry 解決**（クロス dept  worker 対応）。

## レビュー NG 時（修正タスク）

[`pm-review-rework-ssot.md`](pm-review-rework-ssot.md) · CLI: `python tools/pm_create_fix_subtask.py --parent <GID> --review-json output/analysis/reviews/<file>.json [--fix-assignee <slug>] -y`

## 実行エージェントの起動例

```
あなたは data-engineer スキルです。Asana タスク GID ○○ の notes を読み、
担当が data-engineer であることを確認してから作業し、完了前に comment_task.py を実行してください。
```

## 参照

- **dispatch prompt:** [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md#analysis)
- **worker dispatch:** [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md)
- **review NG → 修正タスク:** [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)
- [`analysis-delivery-io.md`](analysis-delivery-io.md)
- [`agent-asana-comment-signature.md`](agent-asana-comment-signature.md)
- [`skills/analysis/analytics-pm/SKILL.md`](../../skills/analysis/analytics-pm/SKILL.md)
