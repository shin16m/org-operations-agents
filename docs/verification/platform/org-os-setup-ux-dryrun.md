# org-os セットアップ UX dryrun（A1 + A2）

> **履歴（RETIRED · 2026-06-09）** — Asana **自動化** / org-os の検証記録。本番は [chat-driven-ops.md](../../design/chat-driven-ops.md)（和久桶チャット入口 · Asana タスク運用継続）。


| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-07 |
| プロジェクト | `1214771428861230` |
| エピック | A1 `1215473523834260` · A2 `1215473524444431` |
| 実行者 | development / workflow-orchestrator |

## 手順

```powershell
# A1: 初回セットアップ
.\scripts\org-ops\setup.ps1 -SkipVenv
.\.venv\Scripts\python.exe .\tools\org_os.py doctor
.\.venv\Scripts\python.exe .\tools\org_os.py doctor --online

# A2: CF 一括同期 + legacy epic スキャン
.\.venv\Scripts\python.exe .\tools\sync_all_cf_env.py --project 1214771428861230 --dry-run
.\.venv\Scripts\python.exe .\tools\backfill_epic_os_state.py --project 1214771428861230 --dry-run
.\.venv\Scripts\python.exe .\tools\org_os.py watch --project 1214771428861230 --once
```

## 結果

| コマンド | exit | 要点 |
|----------|------|------|
| `setup.ps1 -SkipVenv` | 0 | doctor PASS |
| `doctor` | 0 | 15 required keys present |
| `doctor --online` | 0 | CF enum SSOT 一致 · backfill candidates=0 |
| `sync_all_cf_env.py --dry-run` | 0 | org-os / task type / assignee type 3 本成功 |
| `backfill_epic_os_state.py --dry-run` | 0 | scanned=202 · init=0 · ok=6 |
| `watch --once` | 0 | ready/waiting 一覧表示 |

## 受入（★4）

- [x] doctor → sync 案内 → `watch --once` まで 1 フローで到達
- [x] legacy epic 混在プロジェクトで backfill dry-run が動作
- [x] `sync_all_cf_env.py` で CF 同期が 1 コマンド化
- [x] チェックリスト [`docs/setup/asana-cf-checklist.md`](../../setup/asana-cf-checklist.md) 整備

## 備考

本プロジェクトは A1 完了後のため backfill 対象 0 件（想定どおり）。legacy Epic テストは別プロジェクトで再実施可。
