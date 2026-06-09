# Asana ドリブン Phase 2 — development dryrun 記録

> **履歴（RETIRED · 2026-06-09）** — Asana **自動化** / org-os の検証記録。本番は [chat-driven-ops.md](../../design/chat-driven-ops.md)（和久桶チャット入口 · Asana タスク運用継続）。


| エピック | `1215087157303128` |
| development 子 | `1215087017888498` |
| ブランチ | `feature/asana-driven-ops` |
| 実施日 | 2026-05-24 |

## 実装

| ファイル | 内容 |
|----------|------|
| `tools/asana_ops_poller.py` | `--projects` · `--gate-kind` record-wait · RESUME snippet |
| `tools/check_workflow_suspend.py` | resumable hint · pm_emit_resume_prompt 案内 |
| `tools/pm_emit_resume_prompt.py` | **新規** — RESUME 再開 snippet |

## コマンド

```powershell
$env:PYTHONIOENCODING="utf-8"
python tools/asana_ops_poller.py --once --dry-run --human
python tools/asana_ops_poller.py --once --dry-run --projects 1214771428861230
python tools/pm_emit_resume_prompt.py --list
python tools/check_workflow_suspend.py --list
python tools/validate_org_registry.py
python tools/validate_ssot_contract.py
python tools/validate_fixture_schemas.py
```

## 結果

| チェック | 結果 |
|----------|------|
| poller dry-run | exit 0 |
| pm_emit_resume_prompt | exit 0 |
| validate 3 本 | OK |

## 参照

- UX: `output/ux/specs/1215087017928843-ux-spec.md`
- 要件: `output/development/requirements/1215087017888498-requirements.md`
