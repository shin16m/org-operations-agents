# マイルストーン自律評価 — Asana 起票記録

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-09 |
| プロジェクト | `1214771428861230`（エージェント組織構築） |
| セクション | **組織構築** `1215082835252574` |
| Handoff SSOT | [`docs/verification/fixtures/planning/handoff/milestone-self-assessment.json`](../../fixtures/planning/handoff/milestone-self-assessment.json) |

## 親エピック

| 項目 | 値 |
|------|-----|
| GID | `1215534306691804` |
| URL | https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1215534306691804 |
| Task Type | Epic |
| OS State | Ready |

## 子タスク（Execution Order 順）

| 順 | GID | タイトル | department |
|----|-----|----------|------------|
| 1 | `1215534237017006` | milestone-effectiveness-standard.md — 実効達成度 SSOT | governance |
| 2 | `1215534228429509` | MilestoneEffectivenessReport schema v1 | governance |
| 3 | `1215534228545951` | マイルストーン checklist fixture — M4/M5/M6 テンプレ | governance |
| 4 | `1215534228429497` | [MS1] 定義整備 — マイルストーン | governance |
| 5 | `1215534312180580` | check_milestone_readiness.py — 機械検証 CLI v1 | development |
| 6 | `1215534312353798` | validate_ssot_contract — milestone-readiness 節 | development |
| 7 | `1215534420179424` | [MS2] 機械検証 — マイルストーン | governance |
| 8 | `1215534228741131` | governance-pm SKILL — トラッカー complete 前 readiness 必須 | governance |
| 9 | `1215534312423348` | epic_milestone_readiness_hook.py — complete 前ブロック | development |
| 10 | `1215534236257094` | MS3 dryrun — M5 トラッカー再評価デモ記録 | governance |
| 11 | `1215534312270745` | [MS3] 運用組込み — マイルストーン | governance |
| 12 | `1215534312408819` | completion-100-roadmap — トラッカー実効 done_when 更新 | governance |
| 13 | `1215534236772769` | マイルストーン tracker 用 audit 子テンプレ | governance |
| 14 | `1215534236862465` | マイルストーン readiness — audit 整合監査 dryrun | audit |
| 15 | `1215534236862106` | [MS4] ロードマップ適用 — マイルストーン | governance |
| 16 | `1215534605348980` | emit_milestone_effectiveness_report.py | development |
| 17 | `1215534312334510` | create_milestone_followup_subtasks.py | development |
| 18 | `1215534311738558` | workflow-orchestrator — マイルストーン締め手順 SSOT | governance |
| 19 | `1215534236786944` | run_all_teams_dryrun — milestone-readiness 節 | development |
| 20 | `1215534419646943` | [MS5] 自律ループ完結 — マイルストーン | governance |

Asana dependency は Handoff 配列順（1→2→…→20）で設定済み。

## 再投入

```powershell
$env:ASANA_SECTION_ID = "1215082835252574"
$env:ASANA_PROJECT_ID = "1214771428861230"
python skills/platform/asana-buddy/optional/handoff_to_asana.py `
  --handoff docs/verification/fixtures/planning/handoff/milestone-self-assessment.json `
  -y --if-not-exists --parent 1215534306691804
```

## MS1 達成（2026-06-09）

- 子 1–3 + トラッカー `1215534228429497` complete
- 記録: [`milestone-self-assessment-ms1-delivery.md`](milestone-self-assessment-ms1-delivery.md)

## MS2 達成（2026-06-09）

- 子 5–6 + トラッカー `1215534420179424` complete
- 記録: [`../platform/milestone-self-assessment-ms2-delivery.md`](../platform/milestone-self-assessment-ms2-delivery.md)

## MS3 達成（2026-06-09）

- 子 8–10 + トラッカー `1215534312270745` complete
- 記録: [`../platform/milestone-readiness-ms3-dryrun.md`](../platform/milestone-readiness-ms3-dryrun.md)

## MS4 達成（2026-06-09）

- 子 12–14 + トラッカー `1215534236862106` complete
- completion-100-roadmap.json M4–M9 トラッカー実効 done_when 更新 · Asana sync
- 記録: [`../audit/milestone-readiness-audit-delivery.md`](../audit/milestone-readiness-audit-delivery.md)

## MS5 達成（2026-06-09）

- 子 16–19 + トラッカー `1215534419646943` complete
- emit_report · followup CLI · orchestrator SSOT · all-teams-dryrun 節

## 関連（M5.1 済）

学習ループ個別修復は別 Epic で **2026-06-09 完了済み**（親 `1215534016644254` · OS State=Done）。

記録: [`../platform/m5.1-retro-loop-followup-intake.md`](../platform/m5.1-retro-loop-followup-intake.md)

## 着手順

1. ~~**MS1–MS5**~~ — 完了
2. ~~**M5.1**~~ — 別 Epic で完了
3. **親 Epic** `1215534306691804` — 依頼者確認後 complete 可
4. **完成度100%ロードマップ M6** — 子 3 `1215475359998592` から
