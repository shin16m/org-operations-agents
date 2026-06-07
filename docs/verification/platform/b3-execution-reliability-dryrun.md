# B3 execution reliability — 統合 E2E dryrun

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-07 |
| プロジェクト | `1214771428861230` |
| エピック | B3 `1215473464212013` |
| 方式 | dry-run + unittest |

## 変更ファイル（B3）

| ファイル | 内容 |
|----------|------|
| `tools/execution_stuck_escalate.py` | Running + 企画完了後 stuck → WARN / ESCALATE |
| `tools/execution_resume_scan.py` | stuck 検知を scan ループに統合 |
| `tools/test_execution_kick_guard.py` | Ready 時 BLOCKED 回帰 |
| `tools/test_planning_stuck.py` | ESCALATE 回帰 |
| `docs/design/approval-flow.md` | §5.5 max_ng runbook |

## unittest

```powershell
$env:PYTHONIOENCODING = "utf-8"
python -m unittest tools.test_execution_kick_guard tools.test_planning_stuck tools.test_execution_resume_scan -v
```

## runner 1 サイクル dryrun

```powershell
python tools/asana_ops_runner.py --once --dry-run --human --project 1214771428861230
```

## 期待語彙（B3 追加分）

| 語彙 | フェーズ |
|------|----------|
| `BLOCKED  execution_kick` | Waiting/Ready 時 kick 禁止 |
| `RUNNER  BLOCKED` | runner が blocked 件数を集約 |
| `WARN  execution_stuck` | Running stuck 検知（閾値未満） |
| `ESCALATE parent=...  phase=execution_stuck` | N サイクル stuck 上限 |
| `EXECUTION` / `EXECUTION_DONE` | L3b scan |

## ガード E2E（B3-1）

`execution_kick_guard` は `os_state != Running` または `planning_child_open` で kick を拒否する。

```powershell
python tools/execution_resume_scan.py --project 1214771428861230 --dry-run
# Waiting epic がある場合: RUNNER  BLOCKED  reason=epic_state=Waiting
```

## stuck 検知（B3-2）

| 条件 | 出力 |
|------|------|
| 企画完了 · OS=Running · execution 子なし | `WARN execution_stuck` → N 回で `ESCALATE` |
| 企画完了 · needs_pm_kick · no_worker_subs | 同上 |

環境変数: `ORG_OPS_MAX_EXECUTION_STUCK_CYCLES`（既定 `5`）

## 1 epic 通し参照

L3b 実例 epic `1215436815983476` · PM 子 `1215437076682690` — 詳細は [`watch-auto-l3b-execution-chain-delivery.md`](watch-auto-l3b-execution-chain-delivery.md) · bridge dryrun は [`b3-pm-worker-complete-bridge-dryrun.md`](b3-pm-worker-complete-bridge-dryrun.md)

## 関連

- SSOT: [`docs/design/asana-driven-ops.md`](../../design/asana-driven-ops.md)
- max_ng runbook: [`docs/design/approval-flow.md`](../../design/approval-flow.md) §5.5
