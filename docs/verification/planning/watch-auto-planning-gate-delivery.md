# watch auto planning gate — delivery 記録

| 項目 | 内容 |
|------|------|
| 実施 | 2026-06-04 |
| 親エピック GID | `1215423786532969` |
| ソース intake | `1215418535230639` |
| Handoff | `output/planning/handoff/handoff.watch-auto-planning-gate.json` |

## 子タスク

| # | GID | department | 状態 |
|---|-----|------------|------|
| 1/5 企画 | `1215419774780624` | planning | complete |
| 2/5 開発 | `1215419756956541` | development | complete |
| 3/5 開発 | `1215419756918061` | development | complete |
| 4/5 組織改善 | `1215423787916987` | governance | complete |
| 5/5 監査 | `1215419756047617` | audit | complete |

## 本体変更

| ファイル | 内容 |
|----------|------|
| `tools/asana_ops_poller.py` | `_log_kick_subprocess` · `WARN planning_stuck` · kick 失敗時 planning snippet |
| `tools/cursor_epic_dispatch.py` | 例外時 exit 1 · SKIP exit 2 · HINT  stderr |
| `docs/design/asana-driven-ops.md` | § bootstrap と planning gate |

## 検証

```powershell
# SKIP + HINT（API key なし）→ exit 2
python tools/cursor_epic_dispatch.py --epic 1215423786532969 --mode planning --planning-child 1215419774780624 -y

# poller dry-run（planning stuck WARN）
python tools/asana_ops_poller.py --once --project 1214771428861230 --dry-run --human

python tools/validate_org_registry.py
python tools/validate_fixture_schemas.py
python tools/validate_ssot_contract.py
```

## 監査結果

| 成果物 | パス | status |
|--------|------|--------|
| ConsistencyAuditReport | `output/audit/reports/1215419756047617-consistency.json` | passed |
| AuditReviewResult | `output/audit/reviews/1215419756047617-audit-review.json` | passed |

## 教訓

- **bootstrap ≠ gate** — `watch-auto` だけでは【承認】は出ない（`auto_intake_runner` NOTE 参照）
- **Windows kick** — SDK 失敗時は poller HINT + 手動 planning-pm が正規ルート
