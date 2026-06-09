# マイルストーン実効達成度 — SSOT

| 版 | 1.0 |
| 日付 | 2026-06-09 |
| 適用 | ロードマップ節目トラッカー（`[M4]` `[M5]` `[MSn]` 等）· governance 締め |
| Epic | `1215534306691804` |

## 目的

**作業 Epic の子 complete** と **マイルストーン意図の達成** を区別し、依頼者の振り返り依頼なしで達成度を評価・改善するための SSOT。

M5 で露呈した問題: トラッカーは ✅ だが学習ループ中核（gate CLI 等）が動かない状態があった。

## 用語

| 用語 | 定義 |
|------|------|
| **作業 Epic** | 実装・SSOT 変更を担う子 Epic（例: retro Phase 2 `1215475084856660`） |
| **トラッカー** | 節目確認用タスク（例: `[M5] 学習ループ閉鎖`）。`department: governance` · 多くは doc-only |
| **名目 done_when** | Handoff 上の最小完了条件（子 Epic complete 等） |
| **実効 done_when** | 名目に加え checklist · E2E 記録 · CLI 動作を含む完了条件 |
| **実効スコア** | checklist 加重平均（0–100）。`MilestoneEffectivenessReport.score` |

## 3 軸スコアリング

| 軸 | 重み目安 | 測るもの |
|----|----------|----------|
| **部品（parts）** | 40% | コード・SSOT・unittest が存在し pass |
| **強制（enforcement）** | 30% | opt-in ではなく既定でブロック / 必須化されているか |
| **E2E（e2e）** | 30% | dryrun 記録 · 実 Asana 完走 · plan 展開の証跡 |

各 checklist 項目に `weight` を付け、pass / fail / skip で加重平均する。

## 閾値

fixture の `min_score_achieved`（既定 80）· `min_score_warn`（既定 70）で判定する。

| スコア | 判定 | 動作（MS3 以降） |
|--------|------|------------------|
| **≥ 80** | 達成 | トラッカー complete 可 |
| **70–79** | 警告 | complete 可（MS3）/ 不可（MS4+ 推奨）。改善子起票推奨 |
| **< 70** | 未達 | トラッカー complete **禁止**。follow-up 子を起票 |

環境変数 `ORG_OPS_MILESTONE_READINESS_BLOCK=1` 時は **< 80 で exit 1**（[`epic_milestone_readiness_hook.py`](../../tools/epic_milestone_readiness_hook.py) · MS3）。

## トラッカー vs 作業 Epic

```
作業 Epic 完了  →  部品は揃った可能性
       ↓
check_milestone_readiness（checklist）
       ↓
実効スコア ≥ 閾値  →  トラッカー complete
```

**禁止:** 作業 Epic の子 complete のみでトラッカーを閉じる（名目 done_when のみ）。

## 機械検証

```powershell
python tools/check_milestone_readiness.py `
  --checklist docs/verification/fixtures/milestone-readiness/m5-learning-loop.json `
  [--work-epic-gid 1215475084856660] `
  [--out output/governance/milestone-reports/<tracker_gid>.json]
```

出力: [`MilestoneEffectivenessReport`](../../skills/governance/governance-reviewer/schemas/milestone-effectiveness-report.v1.schema.json)

## checklist fixture

| マイルストーン | fixture |
|----------------|---------|
| M4 Enforcement | [`m4-enforcement.json`](../verification/fixtures/milestone-readiness/m4-enforcement.json) |
| M5 学習ループ | [`m5-learning-loop.json`](../verification/fixtures/milestone-readiness/m5-learning-loop.json) |
| M6 KPI 実測 | [`m6-kpi-measurement.json`](../verification/fixtures/milestone-readiness/m6-kpi-measurement.json) |

## governance-pm 手順（トラッカー締め）

1. 作業 Epic 全子 complete を確認
2. `check_milestone_readiness.py` を実行しレポート保存
3. スコア < 80 → complete せずギャップを comment · follow-up 起票
4. スコア ≥ 80 → `MilestoneEffectivenessReport` を添えて comment → complete

詳細: [`skills/governance/governance-pm/SKILL.md`](../../skills/governance/governance-pm/SKILL.md)（MS3 で追記）

## 関連

- 納品完成度（成果物）: [`delivery-completion-standard.md`](delivery-completion-standard.md)
- セッション教訓: [`output/platform/session-handoff/2026-06-08-completion-roadmap-m4-m5.md`](../../output/platform/session-handoff/2026-06-08-completion-roadmap-m4-m5.md)
- Handoff: [`milestone-self-assessment.json`](../verification/fixtures/planning/handoff/milestone-self-assessment.json)
