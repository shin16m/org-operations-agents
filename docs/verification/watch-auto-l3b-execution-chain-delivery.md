# watch-auto L3b execution chain — 開発 delivery（Phase A–D）

| 項目 | 内容 |
|------|------|
| PM 子 GID | `1215437076682690` |
| 実施 | 2026-06-05 |

## 変更ファイル

| ファイル | Phase |
|----------|-------|
| `tools/cursor_epic_dispatch.py` | A — execution prompt に `--kick -y` |
| `tools/execution_resume_scan.py` | B — Running epic 状態機械 + runner kick |
| `tools/pm_worker_complete_bridge.py` | C — PM complete bridge kick |
| `tools/asana_ops_runner.py` | B/D — `scan_execution_and_kick` 統合 |

## 検証

```powershell
$env:PYTHONIOENCODING = "utf-8"
python -m unittest tools.test_execution_resume_scan tools.test_planning_stuck -v
python tools/execution_resume_scan.py --epic 1215436815983476
python tools/asana_ops_runner.py --once --dry-run
```

## 期待する EXECUTION_SCAN 状態（本 epic · dev 子進行中）

- review complete 後 · 未 comment worker → `needs_worker_kick`
- worker comment 済 · 未 complete → `needs_pm_complete`
- 全 worker complete · 次 dept 子あり → `task_dispatcher --kick`（needs_pm_kick）
