# org-ops watch 運用 runbook

本番標準入口: [`scripts/org-ops/org-ops-watch.ps1`](../../scripts/org-ops/org-ops-watch.ps1)  
SSOT: [`docs/design/asana-driven-ops.md`](../design/asana-driven-ops.md) §本番標準入口

## 前提

- A1 初回セットアップ完了（[`org-os-first-setup.md`](org-os-first-setup.md)）
- `ASANA_PROJECT_ID` · `ASANA_TOKEN` · org-os CF GID 同期済み

## パターン A — snippet-only（`CURSOR_API_KEY` なし）

人間が Cursor チャットで snippet を貼って再開する運用。

```powershell
.\scripts\org-ops\org-ops-watch.ps1 -Yes -Human
# または
scripts\org-ops\org-ops-watch-yes.cmd
```

| 出力 | 操作 |
|------|------|
| `PLANNING_DISPATCH` / `DISPATCH` | 表示された snippet を **新規 Cursor セッション**へ貼る |
| `HINT` | 提案 CLI を手動実行 |
| `WAIT` | Asana UI で【承認】/【レビュー】を complete 待ち |

`--human`（既定: `-Yes` なし時も付与）で **自動 SDK kick はしない**。

## パターン B — AutoKick（`CURSOR_API_KEY` あり）

```powershell
$env:CURSOR_API_KEY = "<your-key>"
.\scripts\org-ops\org-ops-watch.ps1 -Yes -AutoKick -Interval 60
# または
scripts\org-ops\org-ops-watch-auto.cmd
```

| 条件 | 動作 |
|------|------|
| `ORG_OPS_AUTO_KICK=1` + key あり | `PLANNING_DISPATCH` / execution L3b を SDK kick |
| key なし | `SKIP` — snippet-only にフォールバック |

## 1 サイクル検証（dry-run）

```powershell
.\scripts\org-ops\org-ops-once-dryrun.ps1
```

期待語彙: `RUNNER  cycle_order` · `approval_helper_pass` · `SCAN` · `EXECUTION_DONE`

## 開発者向け（本番以外）

```powershell
python tools/asana_ops_runner.py --once --dry-run --human
python tools/asana_ops_poller.py --once --human   # poller 単体（非推奨・本番外）
```

## 人手 dispatch（fallback）

標準 watch ループ外の例外:

```powershell
python tools/task_dispatcher.py --parent <EPIC_GID> --list
python tools/task_dispatcher.py --parent <EPIC_GID> --dry-run
```

または和久桶さんへチャットで依頼。

## BLOCKED の見方

```
RUNNER  BLOCKED  epic=<GID>  state=<state>  reason=<detail>
RUNNER  execution_blocked  count=N
```

| reason 例 | 意味 |
|-----------|------|
| `epic_state=Ready` | execution kick 前に `org-os dispatch` が必要 |
| `planning_child_open=<GID>` | 企画子が未完了 |

## 関連

- Windows 常駐: [`scripts/org-ops/README.md`](../../scripts/org-ops/README.md)
- E2E 記録: [`docs/verification/platform/b1-planning-execution-kick-dryrun.md`](../verification/platform/b1-planning-execution-kick-dryrun.md)
