# Asana ドリブン Phase 4 auto-intake — dryrun 記録

| 項目 | 内容 |
|------|------|
| エピック | `1215087317688245` |
| 日付 | 2026-05-24 |

## 実施

### SSOT（子【1/5】）

- `docs/design/asana-driven-ops.md` v1.3 Phase 4
- `validate_ssot_contract.py` exit 0

### CLI auto-bootstrap（子【2/5】）

```powershell
python tools/auto_intake_runner.py --task 1215102364986845 --dry-run
python tools/asana_ops_poller.py --once --auto-bootstrap --dry-run
```

- `AUTO_BOOTSTRAP` / `DISPATCH` 行確認

### Cursor SDK PoC（子【3/5】）

```powershell
python tools/cursor_intake_dispatch.py --task 1215102364986845 --dry-run
```

- `CURSOR_API_KEY` 未設定時: `SKIP` · CLI baseline を正とする

### ダッシュボード / record-wait

- planning gate: `--record-wait` → dashboard WAIT
- PM review gate: `--gate-kind pm_review_gate --department development`

## 採否

| 経路 | 採用 |
|------|------|
| CLI `auto_intake_runner` + poller `--auto-bootstrap` | **正（必須）** |
| Cursor SDK `cursor_intake_dispatch` | **optional**（API key · pip install 時のみ） |

## 既知制約

- worker サブタスク CF PUT 400 → `CF=skip`（layout-fix）
- `--record-wait` 未実行時はダッシュボードに gate 待ちが出ない
