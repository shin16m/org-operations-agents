# エピック完了前レトロ → intake タスク化 — dryrun 記録

| 日付 | 2026-05-24 |
| エピック | `1215086241090085` |
| ベースライン | `2efa45a` |

## R1: タスク単位レトロ

| 項目 | 結果 |
|------|------|
| SSOT | `docs/design/task-retrospective-ssot.md` |
| comment 必須節 | `agent-asana-comment-signature.md` — `## レトロスペクティブ` |
| JSON | `record_task_retrospective.py` → `output/platform/retrospectives/<task>-retro.json` |
| [retro] サブ | `create_retro_subtask.py`（ネスト · addProject なし） |
| PM チェック | `check_task_retrospective.py` |

## R3–R6: エピック集約 · intake 承認

| 項目 | 結果 |
|------|------|
| 集約 | `aggregate_epic_retrospective.py` |
| 承認サブ | `create_retrospective_intake_gate.py`（【承認】レトロ改善候補） |
| gate check | `check_retrospective_intake_gate.py` |
| 起票 | `create_retrospective_intake_tasks.py`（gate exit 0 必須） |
| 依頼者コメント | intake タスク notes `## 依頼者コメント` |

## 検証

```powershell
python tools/validate_ssot_contract.py
python tools/validate_org_registry.py
python tools/record_task_retrospective.py --task 000 --agent test --improve "smoke" -y 2>nul || python tools/record_task_retrospective.py --task 000 --agent test --improve smoke
python tools/check_task_retrospective.py --task 000
```

## 運用

- 【承認】/【レビュー】サブは人間 complete（エージェント禁止）
- intake 起票は承認前 CLI が exit 1
