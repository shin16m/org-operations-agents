# エージェント作業 — Asana 署名付きコメント

| 項目 | 内容 |
|------|------|
| 版 | 1.0 |
| 日付 | 2026-05-18 |

## 1. 目的

AI エージェントが Asana タスクを処理した際、**誰（どの agent / skill）が何をしたか**をタスクのストーリー（コメント）に残す。

## 2. 適用可否

| 観点 | 結論 |
|------|------|
| 技術 | **可能** — Asana REST API `POST /tasks/{gid}/stories` でコメント投稿 |
| 運用 | **可能** — 各スキル SKILL に「完了前に `comment_task.py`」を必須化。`complete_task.py` の直前に実行 |
| 強制力 | **部分的** — CLI は人間/エージェントが実行。100% 自動強制はしないが、未コメントは PM チェックで検知 |

## 3. 署名ブロック（必須）

コメント先頭に YAML 風メタデータを置く（Asana 上はプレーンテキスト）。

```text
---
🤖 agent-work-record
agent: developer
skill: skills/development/developer/SKILL.md
phase: complete
executed_at: 2026-05-18T14:30:00+09:00
---

## 実施内容
（何をしたか）

## 成果物
- path/to/file.md

## 補足
（任意）
```

| フィールド | 必須 | 説明 |
|------------|------|------|
| `agent` | はい | [`agent-registry.yaml`](../../workflows/agent-registry.yaml) の `slug` |
| `skill` | はい | スキルパス（例 `skills/development/developer/SKILL.md`） |
| `phase` | いいえ | `start` \| `complete`（省略時 `complete`） |
| `executed_at` | いいえ | ISO 8601（省略時は CLI が付与） |

## 4. AgentWorkComment JSON（機械可読）

スキーマ: [`skills/platform/asana-buddy/schemas/agent-work-comment.v1.schema.json`](../../skills/platform/asana-buddy/schemas/agent-work-comment.v1.schema.json)

```json
{
  "schema_version": "1.0",
  "task_gid": "1214877045257081",
  "agent": "developer",
  "skill_path": "skills/development/developer/SKILL.md",
  "phase": "complete",
  "summary": "要件に沿い API ヘルパを実装",
  "body_markdown": "## 実施内容\n...",
  "artifacts": ["skills/platform/asana-buddy/optional/comment_task.py"]
}
```

## 5. 投稿タイミング

| ロール | タイミング | phase |
|--------|------------|-------|
| doc-writer / developer / reviewer | 委譲作業完了・PM/reviewer へ提出前 | `complete` |
| product-manager | 子タスクを Asana 完了にする直前 | `complete` |
| plan-reviewer | Handoff レビュー結果を返す前（対象タスクがある場合） | `complete` |
| workflow-orchestrator | gate 判定・エピック完了報告前（親/子に記録する場合） | `complete` |
| task-dispatcher | 配賦プロンプト返却のみの場合は不要。実作業後は担当スキルが投稿 | — |

## 6. 完了との順序（必須）

```
comment_task.py  →  complete_task.py -y  →  DeptWorkComplete（チーム内）
```

コメントなしで `complete_task.py` だけ実行しない。

## 7. CLI

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py `
  --gid <TASK_GID> `
  --agent developer `
  --skill skills/development/developer/SKILL.md `
  --summary "実装完了" `
  --body-file .\work-comment-body.md `
  -y
```

JSON から:

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py --from-json .\output\platform\comment.example.json -y
```

## 8. 制限

- Asana API トークンにストーリー作成権限が必要
- コメントは削除・編集の監査は Asana 標準に従う
- モデル名（GPT 等）は任意フィールド `model` で追記可能だが必須ではない
