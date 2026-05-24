# エージェント作業 — Asana 署名付きコメント

| 項目 | 内容 |
|------|------|
| 版 | 1.1 |
| 日付 | 2026-05-23 |

## 1. 目的

AI エージェントが Asana タスクを処理した際、**誰（どの agent / skill）が何をしたか**をタスクのストーリー（コメント）に残す。**依頼者（タスクオーナー）が Asana だけで経緯を追える**ことを目的に、本文の粒度も本書で規定する。

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

## 4. 依頼者向け本文ガイド（必須）

署名ブロックの下（`--body` / `body_markdown`）は、**依頼者がタスク一覧から開いて理解できる**ことを優先する。

### 4.1 分量

| 指標 | 目安 |
|------|------|
| 本文（署名除く） | **150–350 日本語字** |
| 箇条書き | **2–5 項目**（1 項目 1 行〜2 行） |
| 超過時 | 詳細は成果物パスへ委譲し、コメントは要約 + リンクのみ |

### 4.2 必須セクション

| セクション | 必須 | 内容 |
|------------|------|------|
| `## 要約` | はい | 1 行（`--summary` と同趣旨。CLI が自動付与する場合あり） |
| `## 実施内容` | はい | 何をしたか（箇条書き） |
| `## 判断・理由` | 条件付き | レビュアー / PM gate / 差し戻し時は**必須** |
| `## 成果物` | 条件付き | ファイルパス・JSON・子 GID 等（あれば） |
| `## 次の状態` | 推奨 | 依頼者が次に見るべきタスク・待ち状態 |

**避ける:** 「完了しました」のみ / dryrun 用の一行メモ / 内部 slug だけの羅列。

### 4.3 良い例・悪い例

**悪い（短すぎ）:**

```text
handoff.all-teams-dryrun.json を出力。
```

**良い（依頼者が追える）:**

```text
## 実施内容
- 全チーム dryrun 用 Handoff JSON を作成（epic + execution 系 4 子）
- schema_version 1.2、各 subtask に department を付与

## 成果物
- docs/verification/fixtures/planning/handoff/handoff.all-teams-dryrun.json

## 次の状態
- plan-reviewer の PlanReviewResult 待ち（同一企画子 GID）
```

## 5. ロール別テンプレ

### 5.1 ワーカー（requirements-writer / developer / ux-designer / data-* 等）

```markdown
## 実施内容
- （サブ notes の done_when に対応した作業 2–4 項目）

## 成果物
- output/<team>/...（相対パス）

## 次の状態
- {pm_slug} がサブタスクを complete し、次フェーズへ dispatch
```

### 5.2 レビュアー（plan-reviewer / dev-reviewer / ux-reviewer / analysis-reviewer）

```markdown
## 実施内容
- （レビュー対象）を確認
- 判定: passed / passed_with_notes / failed

## 判断・理由
- （主要 finding 1–2 件。failed 時は必須）

## 成果物
- output/.../reviews/<file>.json

## 次の状態
- passed* → PM が gate または次工程へ
- failed → PM が修正サブタスクを新規作成
```

### 5.3 チーム PM（planning-pm / product-manager / ux-pm / analytics-pm / audit-pm）

```markdown
## 実施内容
- 子サブタスク N 件を dispatch / 完了集約
- （親子の Asana 状態変更）

## 判断・理由
- （gate 承認・profile 決定・差し戻し理由など）

## 成果物
- DeptWorkComplete · artifacts[]

## 次の状態
- 統括グループへ DeptWorkComplete 提出 / 次チーム dispatch 待ち
```

## 6. AgentWorkComment JSON（機械可読）

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

## 7. 投稿タイミング

| ロール | タイミング | phase |
|--------|------------|-------|
| ux-designer / ux-reviewer | 委譲作業完了・PM へ提出前 | `complete` |
| requirements-writer / tech-designer / developer / dev-reviewer / qa-verifier | 委譲作業完了・PM へ提出前 | `complete` |
| consistency-auditor / audit-reviewer | 委譲作業完了・PM へ提出前 | `complete` |
| product-manager | 子タスクを Asana 完了にする直前 | `complete` |
| plan-reviewer | Handoff レビュー結果を返す前（対象タスクがある場合） | `complete` |
| workflow-orchestrator | エピック完了報告前（親/子に記録する場合） | `complete` |
| task-dispatcher | 配賦プロンプト返却のみの場合は不要。実作業後は担当スキルが投稿 | — |

## 8. 完了との順序（必須）

```
comment_task.py  →  complete_task.py -y  →  DeptWorkComplete（チーム内）
```

コメントなしで `complete_task.py` だけ実行しない。

## 9. CLI

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

## 10. 制限

- Asana API トークンにストーリー作成権限が必要
- コメントは削除・編集の監査は Asana 標準に従う
- モデル名（GPT 等）は任意フィールド `model` で追記可能だが必須ではない
