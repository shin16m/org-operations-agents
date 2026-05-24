# 全チーム dryrun — 実行記録

実施: 2026-05-24 12:08 UTC（v3 · 6 チーム）

## 目的

6 L3 チーム（planning / ux / analysis / development / governance / audit）+ プラットフォーム配賦で、各 enabled slug が `comment_task` → `complete_task` まで到達することを Asana 上で確認する。

## 実行

```powershell
$env:PYTHONIOENCODING='utf-8'
python tools/run_all_teams_dryrun.py --parent 1215088290598945 --from-dept planning
# governance / audit は PM assign-plan で手動 dryrun（同一セッション）
```

## Handoff

| 種別 | パス |
|------|------|
| bootstrap | `output/planning/handoff/bootstrap.full-teams-dryrun-v3.json` |
| 本番 Handoff | `output/planning/handoff/handoff.full-teams-dryrun-v3.json` |
| PlanReview | `output/planning/plan-review/plan-review.full-teams-dryrun-v3.json` |

## Asana

| 項目 | 値 |
|------|-----|
| 親エピック GID | `1215088290598945` |
| ソース intake | `1215086738998238` |

## 段階別結果

### planning

- child GID: `1215088153174265`
- workers: issue-story-planner, plan-reviewer, planning-pm

### ux

- child GID: `1215088012892545`
- workers: ux-designer, ux-designer, ux-reviewer

### analysis

- child GID: `1215087999305982`
- workers: data-architect, analysis-reviewer, data-engineer, data-steward, data-analyst, data-scientist, ml-engineer, analysis-reviewer

### development

- child GID: `1215087999630685`
- workers: requirements-writer, dev-reviewer, tech-designer, dev-reviewer, developer, dev-reviewer, ux-reviewer, qa-verifier, requirements-writer, dev-reviewer

### governance

- child GID: `1215088058147282`
- workers: ssot-implementer, governance-reviewer, governance-pm

### audit

- child GID: `1215103392062497`
- workers: consistency-auditor, audit-reviewer, audit-pm
- gate: `check_epic_audit_gate` exit 0

## 参加 slug 一覧

analysis-reviewer, analytics-pm, audit-pm, audit-reviewer, consistency-auditor, data-analyst, data-architect, data-engineer, data-scientist, data-steward, dev-reviewer, developer, governance-pm, governance-reviewer, issue-story-planner, ml-engineer, plan-reviewer, planning-pm, product-manager, qa-verifier, requirements-writer, ssot-implementer, task-dispatcher, tech-designer, ux-designer, ux-pm, ux-reviewer, workflow-orchestrator

## 関連

- [`run_all_teams_dryrun.py`](../../tools/run_all_teams_dryrun.py)
- [`handoff.full-teams-dryrun-v3.json`](../../output/planning/handoff/handoff.full-teams-dryrun-v3.json)
- 索引: [`docs/verification/README.md`](README.md)
