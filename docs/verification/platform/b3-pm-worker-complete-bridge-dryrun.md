# B3 pm_worker_complete_bridge — dryrun 記録

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-07 |
| エピック | B3 `1215473464212013` |
| 参照 epic（L3b 実例） | `1215436815983476` |
| PM 子 GID | `1215437076682690` |

## チェーン

```
execution_resume_scan（OS=Running）
  → state=needs_pm_complete
  → pm_worker_complete_bridge.py --parent <PM_CHILD> --sub <WORKER_SUB> --department development -y
  → product-manager が worker サブを complete
  → 次サイクルで task_dispatcher --kick または次 worker kick
```

## dryrun 手順

```powershell
$env:PYTHONIOENCODING = "utf-8"
python tools/execution_resume_scan.py --project 1214771428861230 --dry-run
python tools/pm_worker_complete_bridge.py `
  --parent 1215437076682690 `
  --sub <WORKER_SUB_GID> `
  --department development `
  --dry-run
```

## 期待出力語彙

| 語彙 | 意味 |
|------|------|
| `EXECUTION  epic=...  state=needs_pm_complete` | scan が PM bridge 対象を検知 |
| `BRIDGE  parent=...  sub=...` | bridge CLI 起動 |
| `HINT  execution_kick` | runner dry-run 時の kick コマンド表示 |
| `KICK  execution` | 本番 auto-kick 時 |

## 検証（2026-06-07 · dry-run）

```
EXECUTION_SCAN  project=1214771428861230  dry_run=True  total=<n>
EXECUTION  epic=1215436815983476  state=needs_pm_complete  pm_child=1215437076682690  ...
EXECUTION_DONE  running_total=<n>
```

`pm_worker_complete_bridge --dry-run` は署名 comment がある worker サブで `BRIDGE` 行と PM prompt を出力。署名なしは `SKIP  no signed comment`。

## 関連

- 実装: [`tools/pm_worker_complete_bridge.py`](../../../tools/pm_worker_complete_bridge.py)
- L3b SSOT: [`docs/design/asana-driven-ops.md`](../../design/asana-driven-ops.md) Phase 7
