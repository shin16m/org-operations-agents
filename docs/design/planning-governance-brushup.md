# 企画 → governance 計画ブラッシュアップ — 運用 SSOT

| 版 | 1.0 |
| 日付 | 2026-05-24 |
| エピック | `1215086194042850` |

## 目的

企画 Handoff（`plan_review` 通過後・`pm_gate` 前）を **governance** が精査し、department 配賦・受け入れ基準・実装スコープの過不足を補正する。

**planning gate（人間承認）は 1 回のまま** — ブラッシュアップ後の Handoff を提示してから `handoff_approved` を得る。

## いつ実施するか

| 条件 | 実施 |
|------|------|
| org-meta / 組織運用変更エピック | **必須** |
| 製品機能のみ（development 子のみ） | 任意（planning-pm 判断） |

## 位置づけ（L1 パイプライン）

```
planning: handoff_plan → plan_review
  → governance: plan_brushup（本書）
  → planning: pm_gate → asana_execute
  → execution 系 dispatch …
```

workflow: [`workflows/planning-delivery.yaml`](../../workflows/planning-delivery.yaml) の `plan_brushup` ステップ。

## 観点（governance チェックリスト）

| # | 観点 | 例 |
|---|------|-----|
| 1 | department 配賦 | org-meta は `governance` + `audit`、製品は `development` 等 |
| 2 | 受け入れ基準 | validate / ReviewResult / dryrun が測定可能か |
| 3 | done_when 粒度 | ワーカー 1 セッションで完結するか |
| 4 | スコープ過不足 | Phase 2 を別エピックに分離すべきか |
| 5 | CLI 共通化 | 承認サブ等を既存 helper と統合できるか |

## 出力

| 成果物 | パス | 担当 |
|--------|------|------|
| ブラッシュアップメモ | `output/governance/brushup/<task_gid>-brushup.md` | ssot-implementer |
| 改善版 Handoff（任意） | `output/governance/brushup/<task_gid>-handoff.brushup.json` | ssot-implementer |

**plan_review の再実施は不要。** ブラッシュアップで子 3 以降のスコープを更新する場合は、改善メモに「子 N スコープ更新」を明記し governance 内で完結する。

## 差し戻し

- 企画へ戻す: planning-pm が `handoff_plan` 再実行（plan-reviewer 省略不可）
- governance 内修正のみ: brushup メモで足りる場合は Handoff JSON を直接更新せず改善メモのみ

## Asana 上承認との関係

- **planning gate** = チャットまたは将来 Asana 承認サブ（[`asana-driven-intake` 系は別エピック](asana-driven-intake.md) で統合検討）
- **PM 委譲品質ゲート** = L3 PM の `pm_assign_subtasks` 後（[`pm-assign-review-gate.md`](pm-assign-review-gate.md)）

## 参照

- [`governance-delivery-io.md`](governance-delivery-io.md)
- [`workflow-io-contract.md`](workflow-io-contract.md)
