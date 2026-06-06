# 全チーム dryrun — 実行記録

実施: 2026-06-06 01:06 UTC

## 目的

4 L3 チーム（planning / ux / analysis / development）+ プラットフォーム配賦で、各 enabled slug が `comment_task` → `complete_task` まで到達することを Asana 上で確認する。

## 実行

```powershell
$env:PYTHONIOENCODING='utf-8'
.\tools\run_all_teams_dryrun.py
```

## fixture

| 種別 | パス |
|------|------|
| bootstrap Handoff | `docs/verification/fixtures/planning/handoff/bootstrap.all-teams-dryrun.json` |
| 本番 Handoff | `docs/verification/fixtures/planning/handoff/handoff.all-teams-dryrun.json` |
| PlanReview | `docs/verification/fixtures/planning/plan-review/plan-review.all-teams-dryrun.json` |
| UX assign plan v2 | `skills/ux/examples/assign-plan.dryrun-v2.json` |
| 分析 assign plan v2 | `skills/analysis/examples/assign-plan.dryrun-v2.json` |

## v2 到達確認

| チーム | 追加ロール / 変更 |
|--------|-------------------|
| UX | `design-system-owner`（4 サブ · flagship dryrun） |
| 分析 | `analytics-requirements-writer` が要件 + リリース（10 サブ · full dryrun） |
| 開発 | UX 子完了後、開発子 notes に `## 依存（読み取り専用）` で Figma URL stub を転記 |

## Asana

| 項目 | 値 |
|------|-----|
| 親エピック GID | `1215465900247375` |
| 親 URL | https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1215465900247375 |

## 段階別結果

### planning

- child GID: `1215465850606542`
- workers: issue-story-planner, plan-reviewer, planning-pm

### ux

- child GID: `1215466153211476`
- workers: ux-designer, ux-reviewer, design-system-owner, ux-reviewer

### analysis

- child GID: `1215465851200801`
- workers: analytics-requirements-writer, data-architect, analysis-reviewer, data-engineer, data-steward, data-analyst, data-scientist, ml-engineer, analysis-reviewer, analytics-requirements-writer

### development

- child GID: `1215466153208885`
- workers: requirements-writer, dev-reviewer, tech-designer, dev-reviewer, developer, dev-reviewer, ux-reviewer, qa-verifier, requirements-writer, dev-reviewer

## 参加 slug 一覧

analysis-reviewer, analytics-requirements-writer, data-analyst, data-architect, data-engineer, data-scientist, data-steward, design-system-owner, dev-reviewer, developer, issue-story-planner, ml-engineer, plan-reviewer, planning-pm, qa-verifier, requirements-writer, tech-designer, ux-designer, ux-reviewer

## 関連

- [`run_all_teams_dryrun.py`](../../tools/run_all_teams_dryrun.py)
- [`handoff.all-teams-dryrun.json`](../../docs/verification/fixtures/planning/handoff/handoff.all-teams-dryrun.json)
- UX v2 単体: [`ux-delivery-v2-dryrun.md`](ux-delivery-v2-dryrun.md)
- 分析 v2 単体: [`analysis-delivery-v2-dryrun.md`](analysis-delivery-v2-dryrun.md)
- 分析 profile 別: [`analysis-profile-dryrun.md`](analysis-profile-dryrun.md)
- チーム間継ぎ目: [`ux-to-dev-full-ui-dryrun.md`](ux-to-dev-full-ui-dryrun.md) · [`analysis-to-dev-dryrun.md`](analysis-to-dev-dryrun.md)
- 索引: [`docs/verification/README.md`](README.md)
