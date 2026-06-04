# bootstrap Ready ガード — delivery

| 項目 | 内容 |
|------|------|
| エピック | `1215151059121360` |
| 日付 | 2026-05-26 |

## 概要

bootstrap 直後の `READY`（approval ログなし）を **planning phase** と判定し、poller が execution `DISPATCH` せず `PLANNING_DISPATCH` のみ出力する。

## 変更

| ファイル | 内容 |
|---------|------|
| `tools/wakuoke_resume_scan.py` | READY に `phase=planning` · `planning_child_gid` |
| `tools/asana_ops_poller.py` | `PLANNING_DISPATCH` 行 · RESUME のみ `DISPATCH`+`START` |
| `tools/epic_resolve.py` | `find_open_planning_child` |
| `docs/design/asana-driven-ops.md` | 出力語彙 |
| `docs/design/org-os-product-io.md` | poller 連携 |

## 検証

```powershell
python tools/asana_ops_poller.py --once --project 1214771428861230 --dry-run --human
```

bootstrap 直後 epic: `PLANNING_DISPATCH` のみ（`DISPATCH` なし）。planning gate RESUME 後: `DISPATCH phase=execution`。

## 関連

- Handoff: `output/planning/handoff/handoff.bootstrap-ready-guard.json`
