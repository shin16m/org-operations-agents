# Asana ドリブン Phase 3 + B2 queue — dryrun 記録

> **履歴（RETIRED · 2026-06-09）** — Asana **自動化** / org-os の検証記録。本番は [chat-driven-ops.md](../../design/chat-driven-ops.md)（和久桶チャット入口 · Asana タスク運用継続）。


| エピック | `1215087157410286` · B2 `1215473492047743` |
| development 子 | `1215086999635228` |
| ブランチ | `feature/asana-driven-ops` |
| 実施日 | 2026-05-24（初版）· 2026-06-07（B2 queue 追記） |

## 実装

| ファイル | 内容 |
|----------|------|
| `tools/asana_ops_sessions.py` | sessions 共有 · webhook log · handle_task_completed |
| `tools/asana_webhook_handler.py` | **新規** — POST /webhook dryrun |
| `tools/asana_ops_dashboard.py` | ダッシュボード — sessions · **org-os queue** · runner log tail |

## コマンド

```powershell
$env:PYTHONIOENCODING="utf-8"
python tools/asana_webhook_handler.py --port 8766
python tools/asana_ops_dashboard.py --port 8765
python tools/validate_org_registry.py
python tools/validate_ssot_contract.py
python tools/validate_fixture_schemas.py
```

## Webhook dryrun

```powershell
curl -X POST http://127.0.0.1:8766/webhook -H "Content-Type: application/json" -d "{\"events\":[{\"action\":\"changed\",\"resource\":{\"gid\":\"SUB_GID\",\"resource_type\":\"task\"},\"change\":{\"field\":\"completed\",\"new_value\":true}}]}"
```

## B2 queue API（2026-06-07）

```powershell
python -c "from asana_ops_dashboard import queue_ready_payload, queue_wait_payload; print(queue_ready_payload()); print(queue_wait_payload())"
python tools/asana_ops_dashboard.py --port 8765
# ブラウザ: http://127.0.0.1:8765/ — READY / WAIT 表 + sessions
curl http://127.0.0.1:8765/api/queue/ready
curl http://127.0.0.1:8765/api/queue/wait
```

| API | 結果 |
|-----|------|
| `/api/queue/ready` | JSON · `org_os.queue.ready_queue` |
| `/api/queue/wait` | JSON · `org_os.queue.wait_list` |
| UI refresh 5s | sessions + queue 同時表示 |
| `-Dashboard` on watch.ps1 | runner + dashboard 同時起動 |

## 結果

| チェック | 結果 |
|----------|------|
| webhook handler import | OK |
| dashboard import | OK |
| queue API（project 1214771428861230） | OK |
| validate 3 本 | OK |

## 参照

- UX: `output/ux/specs/1215087283197185-ux-spec.md`
- 要件: `output/development/requirements/1215086999635228-requirements.md`
