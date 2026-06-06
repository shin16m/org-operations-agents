# Asana ドリブン Phase 3 — development dryrun 記録

| エピック | `1215087157410286` |
| development 子 | `1215086999635228` |
| ブランチ | `feature/asana-driven-ops` |
| 実施日 | 2026-05-24 |

## 実装

| ファイル | 内容 |
|----------|------|
| `tools/asana_ops_sessions.py` | sessions 共有 · webhook log · handle_task_completed |
| `tools/asana_webhook_handler.py` | **新規** — POST /webhook dryrun |
| `tools/asana_ops_dashboard.py` | **新規** — ダッシュボード MVP port 8765 |

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

## 結果

| チェック | 結果 |
|----------|------|
| webhook handler import | OK |
| dashboard import | OK |
| validate 3 本 | OK |

## 参照

- UX: `output/ux/specs/1215087283197185-ux-spec.md`
- 要件: `output/development/requirements/1215086999635228-requirements.md`
