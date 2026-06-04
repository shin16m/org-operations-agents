# assign plan 補足 — md Asana 添付（doc-only / 全 profile 共通）

requirements-writer / as-built-spec サブの `done_when` に以下を含める:

```
- output/development/requirements/<sub_gid>-requirements.md を作成
- attach_task_files.py --gid <sub_gid> --file <上記> -y 済み
- comment_task 署名付き投稿済み
```

PM complete 前チェック:

```powershell
python skills/platform/asana-buddy/optional/attach_task_files.py --gid <sub_gid> --list
```

`review_kind=requirements` の dev-reviewer サブ notes に「attach 欠落時 failed」と記載する。
