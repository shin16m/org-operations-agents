# 全チーム dryrun — 実行記録

実施: 2026-05-23

## 目的

4 L3 チーム（planning / ux / analysis / development）+ プラットフォーム配賦で、**各 enabled slug が `comment_task` → `complete_task` まで到達**することを Asana 上で確認する。

## 実行

```powershell
$env:PYTHONIOENCODING='utf-8'
python tools/run_all_teams_dryrun.py
# 開発段階のみ再開（初回 notes 更新失敗後）
python tools/run_all_teams_dryrun.py --parent 1215081453840132 --skip-bootstrap --from-dept development
```

## Asana

| 項目 | GID / URL |
|------|-----------|
| 親エピック | `1215081453840132` |
| 親 URL | https://app.asana.com/1/1214766054680431/project/1215080644653452/task/1215081453840132 |
| 企画子 | `1215081459858377` — **completed** |
| UX 子 | `1215081414806531` — **completed** |
| 分析子 | `1215081453850906` — **completed** |
| 開発子 | `1215081524515224` — **completed** |

---

## 段階別結果

### L1 — プラットフォーム

| step | slug | 結果 |
|------|------|------|
| intake | workflow-orchestrator | 親エピックに comment → complete |
| bootstrap | asana-buddy（`handoff_to_asana.py`） | 親 + 企画子作成 |
| sync | asana-buddy | fuzzy マッチ企画子 + UX/分析/開発子 create |
| dispatch ×4 | task-dispatcher | 各チーム子に dispatch comment |

### L3 — 企画

| slug | 結果 |
|------|------|
| issue-story-planner | Handoff JSON 作成済み → comment |
| plan-reviewer | PlanReview passed_with_notes → comment |
| planning-pm | sync 完了 → comment → **子 complete** |

### L3 — UX（サブタスク 3）

| slug | サブ GID |
|------|----------|
| ux-designer | `1215081415062768`, `1215095955602865` |
| ux-reviewer | `1215081453698664` |
| ux-pm | 親 `1215081414806531` complete |

### L3 — 分析（サブタスク 8）

| slug | 備考 |
|------|------|
| data-architect | 【3/4-1】 |
| analysis-reviewer | 【3/4-2】【3/4-8】 |
| data-engineer | 【3/4-3】 |
| data-steward | 【3/4-4】 |
| data-analyst | 【3/4-5】 |
| data-scientist | 【3/4-6】 |
| ml-engineer | 【3/4-7】 |
| analytics-pm | 親 complete |

### L3 — 開発 full-ui（サブタスク 10）

| slug | 備考 |
|------|------|
| requirements-writer | 【3/4-1】【3/4-9】 |
| dev-reviewer | 【3/4-2】【3/4-4】【3/4-6】【3/4-10】 |
| tech-designer | 【3/4-3】 |
| developer | 【3/4-5】 |
| ux-reviewer | 【3/4-7】 ux_implementation |
| qa-verifier | 【3/4-8】 |
| product-manager | 親 complete · `## 依存` 転記済 |

---

## 参加 slug 一覧（enabled · dryrun 到達）

`workflow-orchestrator`, `asana-buddy`, `task-dispatcher`, `issue-story-planner`, `plan-reviewer`, `planning-pm`, `ux-pm`, `ux-designer`, `ux-reviewer`, `analytics-pm`, `data-architect`, `data-engineer`, `data-steward`, `data-analyst`, `data-scientist`, `ml-engineer`, `analysis-reviewer`, `product-manager`, `requirements-writer`, `tech-designer`, `developer`, `dev-reviewer`, `qa-verifier`

**対象外（意図）:** `agent-creater`（meta）· `doc-writer` / `reviewer`（disabled）

---

## 成果物

| 種別 | パス |
|------|------|
| bootstrap Handoff | `output/planning/handoff/bootstrap.all-teams-dryrun.json` |
| 本番 Handoff | `output/planning/handoff/handoff.all-teams-dryrun.json` |
| PlanReview | `output/planning/plan-review/plan-review.all-teams-dryrun.json` |
| UX stub | `output/dryrun/ux/` |
| 実行スクリプト | `tools/run_all_teams_dryrun.py` |
| assign plan（分析） | `skills/analysis/examples/assign-plan.dryrun-v1.json` |

---

## 所見

1. **PM サブタスク分解** — ux-pm / analytics-pm / product-manager いずれも `pm_assign_subtasks.py` で nested サブ作成 → ワーカー comment/complete → PM が親 complete。
2. **full-ui 依存** — UX 子完了後、development 子 notes に `profile: full-ui` + `## 依存` を転記してから development サブタスク投入。
3. **初回失敗** — `update_task_notes.py --notes` は `--assignee` 必須のため CLI 直呼びは失敗。スクリプト内 API 直呼びに修正済。
4. **v1 dryrun の限界** — `run_all_teams_dryrun.py` は **ワーカーを別エージェントセッションで起動しない**。PM 脚本が全 slug の comment を代投する **wiring 検証**のみ。実 multi-agent は [`pm-worker-dispatch-ssot.md`](../design/pm-worker-dispatch-ssot.md) + `pm_emit_worker_prompt.py` を使う。

---

## チェックリスト

- [x] bootstrap 親 + 企画子
- [x] Handoff sync（UX / 分析 / 開発子 create）
- [x] 企画 3 slug comment + complete
- [x] UX 全サブ + ux-pm 親 complete
- [x] 分析 8 サブ + analytics-pm 親 complete
- [x] 開発 10 サブ + product-manager 親 complete
- [x] 親エピック complete

## dryrun 脚本と `--undo`

`run_all_teams_dryrun.py` 内の `complete_task.py --undo` は **dryrun リセット専用**（PM の review 差し戻しには使わない）。運用: [`pm-review-rework-ssot.md`](../design/pm-review-rework-ssot.md)

## 関連

- [`ux-delivery-v1-dryrun.md`](ux-delivery-v1-dryrun.md)
- [`development-pm-assignment-smoke.md`](development-pm-assignment-smoke.md)
- [`analytics-pm-assignment-smoke.md`](analytics-pm-assignment-smoke.md)
