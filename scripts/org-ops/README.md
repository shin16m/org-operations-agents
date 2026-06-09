# org-ops バッチスクリプト

> **RETIRED（2026-06-09）** — Asana ドリブン自動化（watch · poller · auto-kick）は廃止。  
> **本番標準:** [`docs/design/chat-driven-ops.md`](../../docs/design/chat-driven-ops.md) — 和久桶さん（`workflow-orchestrator`）へのチャット依頼。

## 残存スクリプト

| スクリプト | 用途 |
|------------|------|
| [`setup.ps1`](setup.ps1) | venv · `.env` 初期化（Asana タスク運用の前提） |
| `setup.cmd` | 上記（cmd ラッパー） |
| [`org-ops-dispatch.ps1`](org-ops-dispatch.ps1) | **開発用** — `task_dispatcher.py` 手動（リスト / dry-run / kick） |
| `org-ops-dispatch.cmd` | 上記 |
| `org-ops-start.cmd` | RETIRED 案内のみ |

## 廃止（削除済み · 使用しない）

- `org-ops-watch*` — 常駐 runner
- `org-ops-webhook*` — Webhook 常駐
- `org-ops-dashboard*` — WAIT/RESUME ダッシュボード
- `org-ops-once-dryrun*` — poller dry-run
- `org-ops-stop.ps1` — watch 停止
- `org-ops-dispatch*` — 自動 dispatch fallback

## 代替手順

1. Cursor チャットで **和久桶さん** に自然言語で依頼（[`workflow-orchestrator/SKILL.md`](../../skills/platform/workflow-orchestrator/SKILL.md) 起動例 A）
2. 同一セッションで intake → 企画 → execution dispatch まで進行
3. Asana 連携が必要な場合のみ、セッション内で `handoff_to_asana.py` 等を手動実行
