# スモーク — エージェント署名付き Asana コメント

## 前提

- `.venv` と `ASANA_TOKEN`（[`asana-buddy` README](../../skills/asana-buddy/README.md)）
- テスト用タスク GID（未完了の子タスクで可）

## 1. ドライラン

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\comment_task.py `
  --gid <TASK_GID> `
  --agent developer `
  --skill skills/developer/SKILL.md `
  --summary "スモークテスト" `
  --body "## 実施内容`n署名付きコメントの投稿確認" `
  --dry-run
```

署名ブロック（`agent-work-record`）が先頭に付くことを確認。

## 2. 投稿

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\comment_task.py `
  --gid <TASK_GID> `
  --agent developer `
  --skill skills/developer/SKILL.md `
  --summary "スモークテスト" `
  --body "投稿確認" `
  -y
```

Asana タスクのコメント欄にストーリーが増えること。

## 3. JSON 入力

`work/comment.example.json` を作成して:

```json
{
  "schema_version": "1.0",
  "task_gid": "<TASK_GID>",
  "agent": "product-manager",
  "skill_path": "skills/product-manager/SKILL.md",
  "summary": "JSON 経由のスモーク",
  "body_markdown": "## 実施内容\nJSON から投稿",
  "artifacts": ["docs/design/agent-asana-comment-signature.md"]
}
```

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\comment_task.py --from-json .\work\comment.example.json -y
```

## 4. 完了順序

```powershell
# comment → complete
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\comment_task.py --gid <GID> --agent product-manager --skill skills/product-manager/SKILL.md --summary "完了" --body "comment→complete 順の確認" -y
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\complete_task.py --gid <GID> -y
```
