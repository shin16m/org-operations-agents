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
| 集約 | `aggregate_epic_retrospective.py`（`--parent` 時は Epic 配下サブタスク GID の retro のみ · `--no-subtree-filter` で legacy） |
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

## Phase 2 — assign plan retro 自動同梱（2026-06-08）

| 項目 | 結果 |
|------|------|
| Epic 子 | `1215491517102919` |
| 実装 | `pm_assign_subtasks.py` + `create_retro_subtask.ensure_retro_subtask` |
| schema | plan `include_retro_subtasks` · item `retro: true` |
| 検証 | `python -m unittest tools.test_pm_assign_subtasks_retro` |

```powershell
# opt-in plan 例（dryrun · 実 Asana 不要）
python -m unittest tools.test_pm_assign_subtasks_retro
python -c "from pathlib import Path; import sys; sys.path.insert(0,'skills/platform/asana-buddy/optional'); import pm_assign_subtasks as p; assert p.plan_includes_retro({'include_retro_subtasks': True}, {})"
```

## Phase 2 — epic complete retro gate WARN（2026-06-08）

| 項目 | 結果 |
|------|------|
| Epic 子 | `1215475142748815` |
| 実装 | `epic_retrospective_complete_hook.py` · `complete_task` / `complete_epic_os_state` から呼出 |
| 既定 | missing / pending → Asana WARN comment · exit 0 |
| opt-in block | `ORG_OPS_RETRO_COMPLETE_BLOCK=1` |
| 検証 | `python -m unittest tools.test_epic_retrospective_complete_hook` |

## Phase 2 — aggregate --parent フィルタ（2026-06-08）

| 項目 | 結果 |
|------|------|
| Epic 子 | `1215475085127976` |
| 実装 | `aggregate_epic_retrospective.py --parent` サブツリーのみ集約 |
| 検証 | `python -m unittest tools.test_aggregate_epic_retrospective` |

## Phase 2 — run_all_teams dryrun audit（2026-06-08）

| 項目 | 結果 |
|------|------|
| Epic 子 | `1215491557624250` |
| 実装 | `run_all_teams_dryrun.py` に `audit` 部門 · `assign-plan.org-governance-v1.json` |
| 検証 | `rg audit run_all_teams_dryrun.py` · dept_order に audit |

## Phase 2 — default.yaml suspend/resume（2026-06-08）

| 項目 | 結果 |
|------|------|
| Epic 子 | `1215475097082132` |
| 実装 | `workflows/default.yaml` v5 — suspend / resume steps |
| 検証 | `validate_ssot_contract.py` exit 0 |

## Phase 2 — 依頼者意見必須 · intake stories（2026-06-08）

| 項目 | 結果 |
|------|------|
| Epic 子 | `1215475080245914` · `1215475209626800` |
| 実装 | `create_retrospective_intake_tasks` requester 必須 · `intake_from_asana` requester_comments |
| 検証 | `python -m unittest tools.test_intake_from_asana` |

## Phase 2 — dashboard / pm_assign lite（2026-06-08）

| 項目 | 結果 |
|------|------|
| Epic 子 | `1215475142717078` |
| 実装 | poller `DASHBOARD ready_total` · `execution_resume_scan` `pm_assign_lite_required` hint |
| 検証 | `rg pm_assign_lite_required tools/execution_resume_scan.py` |
