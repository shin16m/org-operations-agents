# ux-pm 厳密運用 — チーム内アサインと Asana 記録

| 版 | 1.2 |
| 日付 | 2026-05-23 |
| 適用 | UX チーム L3（`ux-delivery` v1） |

## 原則

1. **ux-pm は自分で体験設計しない**（進行・タスク分解・artifact 公開・完了集約を除く）。
2. PM が dispatch された子タスクを読み、**必要な作業タスクを洗い出す**。
3. **必須:** 洗い出したタスクを **Asana サブタスク** に分解し、各 notes に **担当 slug** を書く（単一タスクに PM 以外を直接委譲しない）。
4. **担当エージェントだけ**がそのサブタスクを実行する（notes の `担当:` と自分の slug が一致すること）。
5. 完了は **担当の comment_task → PM が当該サブを complete → 全サブ完了後に親を comment → complete**。

**comment_task:** PM slug で ux-designer / ux-reviewer の作業を署名しない。実装作業は notes `担当:` のワーカー slug。

## PM の必須フロー（intake）

```
1. fetch_task.py --gid <親子GID> で notes を読む
2. 完了条件から作業単位を分解（例: 体験設計書 / Design System / ux_spec review）
3. assign plan JSON を work/assign-plans/ または skills/ux/examples/ に残す
4. pm_assign_subtasks.py でサブタスク作成 + 各 担当: 設定
5. **create_pm_review_gate.py** → 人間 complete → **check_pm_review_gate.py exit 0**
6. 親 notes → 担当: ux-pm, 状態: in_progress
7. サブ完了のたびに 4→5 を繰り返し、全サブ完了後に DeptWorkComplete
```

**禁止:** サブタスクを作らず、親タスク notes の `担当:` だけ ux-designer に書き換えて委譲すること。

**dispatch 起動文 SSOT:** [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md#ux)

## notes ヘッダ（必須・先頭）

```markdown
チーム: ux

担当: ux-designer
状態: assigned

```

| フィールド | 値 |
|------------|-----|
| `チーム` | `ux` |
| `担当` | [`agent-registry.yaml`](../../workflows/agent-registry.yaml) の slug（`ux-designer` \| `ux-reviewer`） |
| `状態` | `assigned` \| `in_progress` \| `review` \| `done` |

その下に Handoff 由来の `## 背景` / `## 概要` / `## 完了条件` を置く。

## サブタスク分解（例）

親: `【2/4・UX】Web アプリ体験設計` — **担当: ux-pm**（進行のみ）

| サブ | 担当 | 成果物 |
|------|------|--------|
| 【2/4-1】体験設計書 | ux-designer | `output/ux/specs/<gid>-ux-spec.md` |
| 【2/4-2】Design System | ux-designer | `output/ux/design-system/<gid>-design-system.md` |
| 【2/4-3】仕様 review | ux-reviewer | `output/ux/reviews/<gid>-ux-spec-review.json` |

プラン例: [`skills/ux/examples/assign-plan.web-app-v1.json`](../../skills/ux/examples/assign-plan.web-app-v1.json)

## 委譲先一覧（workflow 段階）

| 段階 | 担当 slug | 備考 |
|------|-----------|------|
| 体験設計書 | ux-designer | サブタスク単位 |
| Design System | ux-designer | 大規模 Epic ではサブ分割推奨 |
| 仕様 review | ux-reviewer | `review_kind: ux_spec` |
| 実装一致 review | ux-reviewer | `review_kind: ux_implementation` — **product-manager** から委譲（UX サブタスク外可） |

## CLI

```powershell
# notes 更新（担当追記）
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\update_task_notes.py `
  --gid <GID> --department ux --assignee ux-designer --status assigned --preserve-body -y

# チーム内サブタスク一括作成（JSON プラン）
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent <親GID> --plan .\skills\ux\examples\assign-plan.web-app-v1.json `
  --department ux --update-parent-assignee ux-pm -y

# 担当確認（ワーカー着手前必須）
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <GID> --show-assignee
```

## L3b — ワーカー dispatch（必須）

```powershell
python tools/pm_emit_worker_prompt.py --parent <親GID> --department ux
```

SSOT: [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md)

## レビュー NG 時（修正タスク）

[`pm-review-rework-ssot.md`](pm-review-rework-ssot.md) · CLI: `python tools/pm_create_fix_subtask.py --parent <GID> --review-json output/ux/reviews/<file>.json -y`

## 実行エージェントの起動例

```
あなたは ux-designer スキルです。Asana タスク GID ○○ の notes を読み、
fetch_task.py --show-assignee で担当が ux-designer であることを確認してから作業し、
完了前に comment_task.py を実行してください。
```

## 参照

- **dispatch prompt:** [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md#ux)
- **worker dispatch:** [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md)
- **review NG → 修正タスク:** [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)
- [`ux-delivery-io.md`](ux-delivery-io.md)
- [`agent-asana-comment-signature.md`](agent-asana-comment-signature.md)
- [`skills/ux/ux-pm/SKILL.md`](../../skills/ux/ux-pm/SKILL.md)
- 分析チーム同等運用: [`analytics-pm-assignment.md`](analytics-pm-assignment.md)
