# 和久桶 intake 三モード — 明文化記録

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-09 |
| 依頼 | 和久桶さん intake に幅を持たせる · マイルストーン 90 点目標の明文化 |
| SSOT | [`docs/design/wakuoke-intake-modes.md`](../../design/wakuoke-intake-modes.md) |

## 変更サマリ

| 領域 | 内容 |
|------|------|
| intake 三モード | 課題受付 · タスク作成依頼 · Epic インプット |
| マイルストーン | 各節目で自己評価（MS1–MS5 組織構築済）· 中間 90 目標 · 最終 90 必須 |
| 更新ファイル | `wakuoke-intake-modes.md`（新規）· `workflow-orchestrator/SKILL.md` · `chat-driven-ops.md` · `workflow-session-io.md` · `milestone-effectiveness-standard.md` · `workflow-intake-required.mdc` · `agent-registry.yaml` |

## 三モード定義

| モード | `intake_mode` | フロー |
|--------|---------------|--------|
| 課題受付 | `natural_language` | intake → bootstrap → planning → Epic |
| タスク作成依頼 | `task_creation_request` | 相談 → 合意 → Epic 起票 |
| Epic インプット | `epic_input` | dispatch のみ（既存 Epic） |

## マイルストーン基準

| 対象 | 基準 |
|------|------|
| 中間 `[MSn]` | **90 点以上を目指す** · 機械閾値 ≥80 で complete 可 |
| 最終 `[MSn]` / 成果物 | **90 点以上を達成**（`min_score_achieved: 90`） |

既存ツール: `check_milestone_readiness.py` · `emit_milestone_effectiveness_report.py` · `epic_milestone_readiness_hook.py`

## 検証

- [x] SSOT 新規作成
- [x] workflow-orchestrator SKILL / README 更新
- [x] chat-driven-ops · workflow-session-io 参照追加
- [x] milestone-effectiveness-standard 90 点節追加
- [x] Cursor rule · agent-registry 更新
