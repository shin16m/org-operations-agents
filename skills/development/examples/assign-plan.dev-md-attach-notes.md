# assign plan 補足 — md Asana 添付（doc-only / 全 profile 共通）

requirements-writer / as-built-spec サブの `done_when` に以下を含める:

```
- output/development/requirements/<PM子GID>-requirements.md を作成（または specs/）
- attach_task_files.py --gid <worker_sub> --also-gid <review_sub> --file <上記> --skip-if-present -y 済み
- review_sub は tools/resolve_dev_review_sub.py --parent <PM子> --review-kind requirements|mismatch で解決
- comment_task 署名付き投稿済み
```

PM complete 前チェック:

```powershell
python skills/platform/asana-buddy/optional/attach_task_files.py --gid <worker_sub> --list
python skills/platform/asana-buddy/optional/attach_task_files.py --gid <review_sub> --list
```

`review_kind=requirements` / `mismatch` の dev-reviewer **review サブ** notes に「attach 欠落時 failed（review サブ `--list`）」と記載する。
