# B1 planning / execution kick E2E dryrun

> **履歴（RETIRED · 2026-06-09）** — Asana **自動化** / org-os の検証記録。本番は [chat-driven-ops.md](../../design/chat-driven-ops.md)（和久桶チャット入口 · Asana タスク運用継続）。


| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-07 |
| プロジェクト | `1214771428861230` |
| エピック | B1 `1215473595838510` |
| 方式 | dry-run（副作用なし） |

## 手順

```powershell
.\scripts\org-ops\org-ops-once-dryrun.ps1
# または
python tools/asana_ops_runner.py --once --dry-run --human --project 1214771428861230
```

## 期待出力語彙（チェックリスト）

| 語彙 | フェーズ |
|------|----------|
| `RUNNER  cycle_order` | サイクル順序 SSOT 表示 |
| `RUNNER  approval_helper_pass` | B — approval_helper |
| `SCAN` / `SKIP` / `CANDIDATE` | bootstrap 走査 |
| `PLANNING_DISPATCH` | planning phase · `next=planning-pm` |
| `DISPATCH` | execution phase · `next=task-dispatcher` |
| `EXECUTION` / `EXECUTION_DONE` | L3b scan |
| `RUNNER  archive` | session archive |
| `RUNNER  cycle  done` | 1 サイクル完了 |

## 実行結果（2026-06-07）

```
RUNNER  cycle  dry_run=True  auto_kick=False  projects=1
RUNNER  cycle_order  approval_helper_pass -> scan_projects -> ...
RUNNER  approval_helper_pass  count=0
SCAN  project=1214771428861230
...
RUNNER  archive  count=0
RUNNER  cycle  done
exit=0
```

## チェーン説明

```
PLANNING_DISPATCH  →  planning-pm kick（bootstrap 後）
  → gate（人間 Asana UI）
  → RESUME / DISPATCH  →  task-dispatcher（execution 子）
  → execution_resume_scan  →  L3b worker kick
```

本 dryrun は **kick 実行なし**（`--dry-run`）。本番は `org-ops-watch.ps1 -Yes` または `-AutoKick`。

## 関連

- SSOT: [`docs/design/asana-driven-ops.md`](../../design/asana-driven-ops.md)
- runbook: [`docs/e2e/org-ops-watch-runbook.md`](../../e2e/org-ops-watch-runbook.md)
