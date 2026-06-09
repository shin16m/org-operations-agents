# Phase 5 orchestration daemon — delivery

> **履歴（RETIRED · 2026-06-09）** — Asana **自動化** / org-os の検証記録。本番は [chat-driven-ops.md](../../design/chat-driven-ops.md)（和久桶チャット入口 · Asana タスク運用継続）。


| 項目 | 内容 |
|------|------|
| エピック | `1215423734965978` |
| 日付 | 2026-06-04 |

## 概要

`asana_ops_runner.py` で poller 相当処理を watch 1 本化。`ORG_OPS_AUTO_KICK` で SDK kick を env 制御。

## 変更

| ファイル | 内容 |
|---------|------|
| `tools/asana_ops_runner.py` | watch · helper pass · auto-bootstrap · resume · archive |
| `tools/asana_ops_sessions.py` | `archive_resumable_sessions` |
| `tools/asana_ops_poller.py` | `_auto_kick_enabled` · `ORG_OPS_AUTO_KICK` |
| `docs/design/asana-driven-ops.md` | Phase 5 節 |

## 検証

```powershell
python tools/asana_ops_runner.py --once --project 1214771428861230 --dry-run --human
python tools/validate_org_registry.py
python tools/validate_ssot_contract.py
```

## Webhook 本番（SLA 外 · 手順のみ）

1. `python tools/asana_webhook_handler.py --port 8766` を systemd / コンテナで常駐
2. Asana Webhook を `/webhook` に向ける（HTTPS reverse proxy 必須）
3. フォールバック: `asana_ops_runner --watch`（ポーリング）

## 関連

- Handoff: `output/planning/handoff/handoff.orchestration-phase5.json`
