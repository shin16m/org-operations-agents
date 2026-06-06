# 和久桶 auto kick — delivery

| 項目 | 内容 |
|------|------|
| エピック | `1215151139429373` |
| 日付 | 2026-05-26 |

## 概要

poller の `PLANNING_DISPATCH` / `DISPATCH` 後、`cursor_epic_dispatch.py` で Cursor SDK kick（optional）。

## 変更

| ファイル | 内容 |
|---------|------|
| `tools/cursor_epic_dispatch.py` | `--mode planning\|execution` |
| `tools/asana_ops_poller.py` | `--cursor-kick` · `HINT`/`KICK` |
| `docs/design/asana-driven-ops.md` | 語彙 |

## 検証

```powershell
python tools/cursor_epic_dispatch.py --epic 1215151139429373 --mode planning --planning-child 1215151139699900 --dry-run
python tools/asana_ops_poller.py --once --project 1214771428861230 --dry-run --human
```

## 関連

- Handoff: `output/planning/handoff/handoff.wakuoke-auto-kick.json`
