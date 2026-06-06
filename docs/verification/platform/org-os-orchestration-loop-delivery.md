# org-os オーケストレーションループ — delivery

| 項目 | 内容 |
|------|------|
| エピック | `1215129936753287` |
| 日付 | 2026-05-26 |

## 概要

`asana_ops_poller --once` が `wakuoke_resume_scan.scan_ready_actions` を呼び、RESUME 時に `org-os dispatch`（syscall.start）と `DISPATCH` 行を出力する。

## 変更

| ファイル | 内容 |
|---------|------|
| `tools/asana_ops_poller.py` | `scan_resume_and_dispatch` · `--no-scan-resume` · `HINT`/`START`/`DISPATCH` |
| `tools/wakuoke_resume_scan.py` | `scan_ready_actions` / `print_scan_actions` 抽出 · dry-run で consume スキップ |
| `docs/design/asana-driven-ops.md` | 出力語彙 + poller 役割更新 |
| `docs/design/org-os-product-io.md` | poller 連携行 |

## 検証

```powershell
python tools/asana_ops_poller.py --once --project 1214771428861230 --dry-run --human
```

期待: `SCAN` → `RESUME`/`READY` → `START`（dry-run）→ `DISPATCH next=task-dispatcher`

**注意:** poller は task-dispatcher まで自動実行しない。`--human` で stderr に snippet。

## 関連

- Handoff: `output/planning/handoff/handoff.os-orchestration-loop.json`
- kernel E2E: `docs/verification/platform/org-os-kernel-e2e-dryrun.md`
