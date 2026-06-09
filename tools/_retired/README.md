# 廃止ツール（Asana 自動化）

**DEPRECATED · RETIRED（2026-06-09）** — [`docs/design/chat-driven-ops.md`](../../docs/design/chat-driven-ops.md)

## 削除済み

| パス | 役割 |
|------|------|
| `tools/asana_ops_poller.py` | Intake 自動検出 · RESUME スキャン |
| `tools/asana_ops_runner.py` | watch 常駐 runner |
| `tools/asana_ops_dashboard.py` | WAIT/RESUME UI |
| `tools/asana_ops_sessions.py` | session JSON |
| `tools/auto_intake_runner.py` | CLI auto-bootstrap（triage 統合） |
| `tools/cursor_intake_dispatch.py` | SDK intake 自動 kick |
| `tools/approval_helper.py` | 承認サブ完了監視 + 親 CF 復帰 |
| `tools/wakuoke_resume_scan.py` | Ready epic 再開スキャン |
| `tools/check_workflow_suspend.py` | SuspendedSession（`--record-wait`） |
| `tools/pm_emit_resume_prompt.py` | RESUME 再開 snippet |
| `tools/bypass_planning_gate.py` | org-os syscall 経由 gate bypass |
| `scripts/org-ops/org-ops-watch*` | watch 起動 |
| `scripts/org-ops/org-ops-webhook*` | Webhook 常駐 |
| `scripts/org-ops/org-ops-once-dryrun*` | poller dry-run |

## 残置・非推奨（手動 · 開発のみ）

| パス | 備考 |
|------|------|
| `tools/execution_resume_scan.py` | L3b kick スキャン（自動化廃止 · 手動 `task_dispatcher --kick` を推奨） |

## 継続（Asana タスク運用）

`handoff_to_asana.py` · `comment_task.py` · `complete_task.py` · `task_dispatcher.py` · `pm_assign_subtasks.py` — [`asana-buddy/SKILL.md`](../../skills/platform/asana-buddy/SKILL.md)
