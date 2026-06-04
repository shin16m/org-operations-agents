# comment readability — before / after（format_signed_comment v1.3）

| 項目 | 内容 |
|------|------|
| SSOT | [`agent-asana-comment-signature.md`](../../design/agent-asana-comment-signature.md) v1.3 |
| コード | [`build_human_comment_body`](../../../skills/platform/asana-buddy/optional/asana_program_common.py) · [`format_signed_comment`](../../../skills/platform/asana-buddy/optional/asana_program_common.py) |

## before（一行メモ · 旧デフォルト）

入力: `--summary "handoff 出力"` · `--body "handoff.agent-comment-readability.json を出力。"`

```text
## 依頼者向け

**担当:** 開発担当
**要約:** handoff 出力

handoff.agent-comment-readability.json を出力。

---
🤖 agent-work-record
...
```

## after（§4 構造 · 自然語）

入力:

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py `
  --gid <GID> --agent developer `
  --skill skills/development/developer/SKILL.md `
  --summary "Handoff JSON を作成しました" `
  --action "企画要件を整理し Handoff JSON を output/planning/handoff/ に保存しました" `
  --action "各 subtask に department と done_when を付与しました" `
  --artifact output/planning/handoff/handoff.agent-comment-readability.json `
  --next-state "plan-reviewer の PlanReviewResult 待ちです" `
  --dry-run
```

出力（抜粋）:

```text
## 依頼者向け

**担当:** 開発担当
**要約:** Handoff JSON を作成しました

## 実施内容

- 企画要件を整理し Handoff JSON を output/planning/handoff/ に保存しました
- 各 subtask に department と done_when を付与しました

## 成果物

- output/planning/handoff/handoff.agent-comment-readability.json

## 次の状態

plan-reviewer の PlanReviewResult 待ちです

---
🤖 agent-work-record
...
```

## プレーン一行の自動整形

入力: `--body "validate スクリプト 3 本を実行しました"`

→ `_normalize_comment_body` が `## 実施内容` + 箇条書きに変換。
