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

### close_intake_source 統合（エピック `1215087997310991` · 2026-05-24）

`auto_intake_runner -y` 成功後、**同一プロセス**で `close_intake_source_task.py` を呼び出す。

**レトロ intake 追跡:** ソース `1215103019709727` · エピック `1215088011649502`（検証・監査子付きクローズ）

```powershell
python tools/auto_intake_runner.py --task <SOURCE_GID> -y
# → posted_story / updated source completed=True
python tools/asana_ops_poller.py --once --project <PROJECT>  # 同一ソースは SKIP duplicate intake
```

| 確認 | 期待 |
|------|------|
| ソースタスク | `completed=true` · epic リンク story あり |
| poller 再スキャン | `SKIP duplicate intake`（`already_intake_source`） |
| poller `--auto-bootstrap` | `auto_intake_runner` 経由で同一挙動 |

### Cursor SDK PoC（子【3/5】）

```powershell
python tools/cursor_intake_dispatch.py --task 1215102364986845 --dry-run
```

- `CURSOR_API_KEY` 未設定時: `SKIP` · CLI baseline を正とする

### ダッシュボード / record-wait

planning gate / PM review gate 到達時は **【承認】/【レビュー】サブ作成だけではダッシュボードに載らない**。必ず `--record-wait` で `output/platform/sessions/` に保存する。

```powershell
# planning gate（Handoff 投入承認）
python tools/asana_ops_poller.py --record-wait <親GID> <【承認】サブGID> <承認サブURL>

# PM review gate
python tools/asana_ops_poller.py --record-wait <PM子GID> <【レビュー】サブGID> <URL> `
  --gate-kind pm_review_gate --department development

python tools/asana_ops_dashboard.py   # port 8765 · WAIT 行を確認
python tools/asana_ops_poller.py --once   # 【承認】complete 後 RESUME 行
```

- `auto_intake_runner` / poller `--auto-bootstrap` は planning gate を**代行しない**（正規分離）
- `DISPATCH hint=...` 行で record-wait 手順を stderr に出力

## 採否

| 経路 | 採用 |
|------|------|
| CLI `auto_intake_runner` + poller `--auto-bootstrap` | **正（必須）** |
| Cursor SDK `cursor_intake_dispatch` | **optional**（API key · pip install 時のみ） |

## 既知制約

- worker サブタスク CF PUT 400 → `CF=skip`（layout-fix）
- `--record-wait` 未実行時はダッシュボードに gate 待ちが出ない
