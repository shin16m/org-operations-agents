# analytics-pm 厳密運用 — チーム内アサインと Asana 記録

| 版 | 1.0 |
| 日付 | 2026-05-23 |
| 適用 | 分析チーム L3（`analysis-delivery`） |

## 原則

1. **analytics-pm は自分で実装しない**（要求定義・進行・完了集約を除く）。
2. PM が子タスクを分析し、**担当エージェントを決め、notes に書く**。
3. 必要なら **子タスクのさらにサブタスク** を Asana に作り、各 notes に担当を書く。
4. **担当エージェントだけ**がそのタスクを実行する（notes の `担当:` と自分の slug が一致すること）。
5. 完了は **担当の comment_task →（サブタスクなら）PM が親を complete**。

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
  --parent <親GID> --plan .\work\assign-plan.task-1.json -y

# 担当確認
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <GID> --show-assignee

# 再着手（完了を戻す）
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\complete_task.py --gid <GID> --undo -y
```

## 実行エージェントの起動例

```
あなたは data-engineer スキルです。Asana タスク GID ○○ の notes を読み、
担当が data-engineer であることを確認してから作業し、完了前に comment_task.py を実行してください。
```

## 再実施（やり直し）

1. 親子タスクを `--undo` で未完了に戻す（または新サブタスクのみ追加）。
2. 旧成果物は `output/analysis/_archive/` に残し、**strict-v2** 以下に新規作成。
3. PM がアサイン計画 JSON を残す（`work/assign-plans/`）。

## 参照

- [`analysis-delivery-io.md`](analysis-delivery-io.md)
- [`agent-asana-comment-signature.md`](agent-asana-comment-signature.md)
- [`skills/analysis/analytics-pm/SKILL.md`](../../skills/analysis/analytics-pm/SKILL.md)
