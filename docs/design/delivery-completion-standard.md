# 納品完成度標準 — 50% vs 80%

| 版 | 1.0 |
| 日付 | 2026-06-08 |
| 適用 | development / ux / analysis → 開発 consume · governance 改善 Epic |
| Epic | `1215474826616152` |

## 目的

「モックは出るが動かない」「fix ループが続く」状態を避け、**依頼者体感の初回完成度を 80% 前後**に揃えるための SSOT 定義。

## 完成度レベル

| レベル | 定義 | 典型状態 |
|--------|------|----------|
| **~50%** | 見た目・文書・静的 review は通るが、README 手順で起動しない・AC 未検証・代表フロー不通 | モック止まり · fixture fallback · serve 後追い |
| **~80%** | 下記「80% 必須条件」をすべて満たす | 依頼者が README のみで主要機能を確認できる |
| **100%** | Should AC 全 pass · 本番運用 · エッジケース完備 | 本番 SLA · polish 完了 |

## 80% 必須条件

1. **起動** — README の起動コマンド 1 本で主要画面/API が応答（developer smoke ログ付き）
2. **AC Must** — 要件定義書の Must AC が 100% 充足（qa verification `evidence[]` 付き）
3. **AC Should** — Should AC の 60% 以上充足（未達は依頼者サマリに明示）
4. **代表フロー** — UX Happy path 1 本（5 ステップ以内）が実装で再現
5. **データ経路** — full-ui + bundle 時は **本番 consume 経路**で qa passed（fixture のみ不可）
6. **fix 上限** — 同一ゲート R3 到達時は依頼者エスカレーション（[`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)）

## ゲートとの対応

| フェーズ | 80% 達成に必要な SSOT |
|----------|------------------------|
| 要件 | [`acceptance-criteria-template.md`](acceptance-criteria-template.md) — AC + 検証コマンド |
| 設計 | tech-designer「実行契約」節 |
| 実装提出 | developer smoke.md（Must AC 実行結果） |
| code review | smoke 欠落 → failed |
| qa | VerificationResult `evidence[]` 必須 |
| fix | R2 同 finding → 上流（requirements/design）差し戻し優先 |

## KPI（epic レトロで集約）

| KPI | 算出 |
|-----|------|
| 初回 qa pass 率 | 初回 verification `passed*` / development 子数 |
| fix 平均ラウンド | `[fix]` サブ数 / ゲート |
| completion_score | Must AC pass 率（worker レトロ必須項目） |

## 関連

- マイルストーン実効達成度（節目トラッカー）: [`milestone-effectiveness-standard.md`](milestone-effectiveness-standard.md)
- 監査記録: [`output/governance/records/1215474835681087-quality-gap-audit.md`](../../output/governance/records/1215474835681087-quality-gap-audit.md)
- 強みの型: [`delivery-strength-pattern.md`](delivery-strength-pattern.md)
- Handoff: [`output/planning/handoff/delivery-quality-80.json`](../../output/planning/handoff/delivery-quality-80.json)
