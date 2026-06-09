# asana_ops_poller RESUME デコード耐性 — dryrun

> **履歴（RETIRED · 2026-06-09）** — Asana **自動化** / org-os の検証記録。本番は [chat-driven-ops.md](../../design/chat-driven-ops.md)（和久桶チャット入口 · Asana タスク運用継続）。


| 項目 | 内容 |
|------|------|
| エピック GID | `1215087877118910` |
| development 子 | `1215102408753145` |
| ソース intake | `1215086510633126` |
| 日付 | 2026-05-24 |

## 再現条件

Windows + `--human` で RESUME 検出時、`pm_emit_resume_prompt.py` の stdout が CP932 等で UTF-8 decode できずポーラが停止。

## 修正

`tools/asana_ops_poller.py`:

- `_subprocess_env()` — `PYTHONIOENCODING=utf-8`
- `_run_capture()` — `errors="replace"` + stdout None ガード + 例外時 WARN のみ
- `_emit_resume_snippet` / `trigger_intake` で使用

## 確認

```powershell
python tools/asana_ops_poller.py --once --human --project 1215102364986851
python tools/validate_ssot_contract.py
```

期待: RESUME 行出力後も exit 0。decode 失敗時は `WARN resume_snippet` のみで scan 継続。
