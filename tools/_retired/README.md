# 廃止ツール（Asana 自動化）

**DEPRECATED · RETIRED（2026-06-09）** — [`docs/design/chat-driven-ops.md`](../../docs/design/chat-driven-ops.md)

## 削除済み

| パス | 役割 |
|------|------|
| `tools/asana_ops_poller.py` | Intake 自動検出 · RESUME スキャン |
| `tools/asana_ops_runner.py` | watch 常駐 runner |
| `tools/asana_ops_dashboard.py` | WAIT/RESUME UI |
| `tools/asana_ops_sessions.py` | session JSON |
| `scripts/org-ops/org-ops-watch*` | watch 起動 |
| `scripts/org-ops/org-ops-webhook*` | Webhook 常駐 |

## 残置・非推奨（手動・opt-in のみ）

| パス | 備考 |
|------|------|
| `tools/approval_helper.py` | opt-in gate の親 CF 復帰（常駐禁止） |
| `tools/wakuoke_resume_scan.py` | Ready epic スキャン（自動化廃止） |
| `tools/execution_resume_scan.py` | L3b kick スキャン（自動化廃止） |
| `tools/check_workflow_suspend.py` | SuspendedSession（`--record-wait` 廃止） |

## 継続（Asana タスク運用）

`handoff_to_asana.py` · `comment_task.py` · `complete_task.py` · `task_dispatcher.py` · `pm_assign_subtasks.py` — [`asana-buddy/SKILL.md`](../../skills/platform/asana-buddy/SKILL.md)
