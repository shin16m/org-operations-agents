# Phase 6 execution automation — delivery

| 項目 | 内容 |
|------|------|
| エピック | `1215412762687733` |
| 日付 | 2026-06-04 |
| 前提 | Phase 5 `fcf5e0b` · runner · ORG_OPS_AUTO_KICK |

## 概要

poller が参照していた `task_dispatcher.py` を実装。L3b は `cursor_worker_dispatch` + `ORG_OPS_AUTO_KICK`。Webhook handler に SLA metrics を追加。

## 変更

| ファイル | 内容 |
|---------|------|
| `tools/task_dispatcher.py` | execution 子 dispatch · prompt SSOT · `--kick` |
| `tools/dispatch_prompt_util.py` | organizations + dispatch-prompt 読込 |
| `tools/cursor_worker_dispatch.py` | PM review gate 後 worker SDK kick |
| `tools/asana_ops_poller.py` | kick 分岐（task_dispatcher / cursor_worker） |
| `tools/asana_webhook_handler.py` | `/metrics` · `/ready` · `WEBHOOK_SLA` · `--require-secret` |
| `tools/cursor_epic_dispatch.py` | execution prompt に task_dispatcher 明示 |
| `docs/design/asana-driven-ops.md` | Phase 6 節 |

## 検証

```powershell
python tools/task_dispatcher.py --parent 1215412762687733 --list
python tools/task_dispatcher.py --parent 1215412762687733 --dry-run
python tools/asana_ops_runner.py --once --dry-run --human
python tools/validate_org_registry.py
python tools/validate_ssot_contract.py
# webhook metrics (別 terminal)
python tools/asana_webhook_handler.py --port 8766
curl http://127.0.0.1:8766/metrics
```

## Webhook SLA（運用）

| 指標 | 目標 | 確認 |
|------|------|------|
| POST 処理 p95 | < 2000 ms | `/metrics` → `latency.p95_ms` |
| 認証 | secret 必須（本番） | `--require-secret` + `ASANA_WEBHOOK_SECRET` |
| 可用性 | 99%（ops） | health `/health` + 外部監視 |

フォールバック: `asana_ops_runner --watch`（ポーリング）

## 関連

- Handoff: `output/planning/handoff/handoff.orchestration-phase6.json`
