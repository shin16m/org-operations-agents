# レトロ / intake Phase 2（M5）— delivery 記録

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-08 |
| 親 Epic | `1215475084856660` |
| ロードマップ M5 トラッカー | `1215475369302645` |
| 参照 | [`retro-intake-phase2-intake.md`](retro-intake-phase2-intake.md) |

## 子タスク完了

| 順 | GID | 実装要点 |
|----|-----|----------|
| 1 | `1215491517102919` | `pm_assign_subtasks` + `ensure_retro_subtask` · plan `include_retro_subtasks` / `retro: true` |
| 2 | `1215475085127976` | `aggregate_epic_retrospective.py --parent` サブツリーフィルタ |
| 3 | `1215475142748815` | `epic_retrospective_complete_hook.py` · complete 前 WARN |
| 4 | `1215491557624250` | `run_all_teams_dryrun.py` audit チーム対応 |
| 5 | `1215475097082132` | `workflows/default.yaml` v5 suspend/resume |
| 6 | `1215475080245914` | `create_retrospective_intake_tasks` 依頼者意見必須（opt-out 可） |
| 7 | `1215475209626800` | `intake_from_asana.py` `requester_comments[]` |
| 8 | `1215475142717078` | `execution_resume_scan` pm_assign lite hint · poller `DASHBOARD ready_total` |

## 検証（M5 出口基準）

```powershell
cd E:\data\document\sourse\org-operations-agents
$env:PYTHONIOENCODING='utf-8'
python tools/validate_ssot_contract.py
python tools/validate_org_registry.py
python -m unittest tools.test_pm_assign_subtasks_retro tools.test_aggregate_epic_retrospective tools.test_epic_retrospective_complete_hook tools.test_intake_from_asana -v
```

| コマンド | 結果 |
|----------|------|
| validate_ssot_contract.py | exit 0 |
| validate_org_registry.py | exit 0 |
| unittest（15 tests） | exit 0 |

## SSOT 更新

| パス | 内容 |
|------|------|
| `docs/design/task-retrospective-ssot.md` | Phase 2 [retro] 自動同梱 · 依頼者意見 |
| `docs/verification/platform/epic-retrospective-intake-dryrun.md` | Phase 2 追記 |
| `workflows/default.yaml` | v5 suspend/resume |
| `tools/run_all_teams_dryrun.py` | audit 部門 |

## M5 マイルストーン

Epic `1215475084856660` 全子 complete + 上記検証 pass → ロードマップ子 `1215475369302645` complete。
