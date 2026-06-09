# watch-auto stuck unblock — delivery

> **履歴（RETIRED · 2026-06-09）** — Asana **自動化** / org-os の検証記録。本番は [chat-driven-ops.md](../../design/chat-driven-ops.md)（和久桶チャット入口 · Asana タスク運用継続）。


| 項目 | 内容 |
|------|------|
| epic | `1215465383602203` |
| 開発子 | `1215465383783963` |
| intake | `1215465107786667` |

## 概要

gate complete 後の B→C gap（既存 runner 修正）に加え、**execution kick ガード**で Waiting / 企画未完了中の L3b 前走りを防止。

## 変更

| ファイル | 変更 |
|----------|------|
| `tools/execution_kick_guard.py` | 新規 |
| `tools/execution_resume_scan.py` | kick 前 BLOCKED |
| `tools/task_dispatcher.py` | `--kick` 前 BLOCKED |
| `tools/cursor_worker_dispatch.py` | epic 解決 + BLOCKED |
| `tools/test_execution_kick_guard.py` | 新規 |
| `docs/design/asana-driven-ops.md` | stuck · 手動 unblock 節 |

## 検証

```powershell
python -m unittest tools.test_execution_kick_guard tools.test_runner_approval_helper_order tools.test_planning_stuck -v
```

## 手動 unblock

```powershell
python tools/approval_helper.py --parent <wait_target> --approval-sub <gate_sub> --gate-kind planning_approval --once
python tools/asana_ops_runner.py --once -y --cursor-kick
```
