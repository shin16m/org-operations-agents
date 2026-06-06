# intake-asana コメント参照 — dryrun 記録

| エピック | `1215101216118327` |
| development 子 | `1215085684762435` |
| intake 元 | `1215082835252595` |
| ソース | `1215082835252595` |

## 手順

```powershell
$env:PYTHONIOENCODING="utf-8"
.\.venv\Scripts\python.exe .\tools\intake_from_asana.py `
  --task 1215082835252595 `
  --out .\output\platform\intake\1215082835252595-snapshot.json
```

## 期待結果

- `schema_version`: `"1.1"`
- `comments[]` — `resource_subtype=comment_added` の story のみ（system 除外）
- `comments_markdown` — 時系列 Markdown 集約
- `--no-comments` で v1.0 互換（comments 省略）

## 実装

- `list_task_comment_stories` in `asana_program_common.py`
- `tools/intake_from_asana.py` v1.1
- `workflow-orchestrator/SKILL.md` — `## ソースコメント` 節ルール
- `docs/design/workflow-session-io.md`

## 参照

- 初回 intake dryrun: [`asana-task-intake-dryrun.md`](asana-task-intake-dryrun.md)
