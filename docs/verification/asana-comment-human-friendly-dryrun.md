# Asana コメント人間向け可読性 — dryrun 記録

| 項目 | 内容 |
|------|------|
| エピック | `1215085682352671` |
| ソースタスク | `1215082835199216` |
| 日付 | 2026-05-24 |

## v1.1 → v1.2 の変更

| 観点 | v1.1 | v1.2 |
|------|------|------|
| 先頭 | YAML 署名 + slug | `## 依頼者向け` + **担当（日本語）** |
| 末尾 | 本文のみ | `agent-work-record` 署名 |
| 表示名 | slug そのまま | [`workflows/agent-display-names.yaml`](../../workflows/agent-display-names.yaml) |

## before（v1.1 · 先頭が機械向け）

```text
---
🤖 agent-work-record
agent: developer
skill: skills/development/developer/SKILL.md
...
---

## 要約
API ヘルパを実装

## 実施内容
- ...
```

## after（v1.2 · 依頼者向けが先）

```text
## 依頼者向け

**担当:** 開発担当
**要約:** API ヘルパを実装

## 実施内容
- ...

---

---
🤖 agent-work-record
agent: developer
...
---
```

## 検証コマンド

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py `
  --gid 1215085926190560 --agent developer `
  --skill skills/development/developer/SKILL.md `
  --summary "二層コメント dryrun" `
  --body-file .\work\sample-comment-body.md --dry-run
```

## 参照

- [`docs/design/agent-asana-comment-signature.md`](../design/agent-asana-comment-signature.md) v1.2
- ソース intake-asana: `1215082835199216`
