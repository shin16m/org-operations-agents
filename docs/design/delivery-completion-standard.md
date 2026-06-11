# 納品完成度標準 — 50% · 80% · 100%

| 版 | 2.0 |
| 日付 | 2026-06-11 |
| 適用 | development / ux / analysis → 開発 consume · governance 改善 Epic |
| Epic | `1215474826616152` · M8 ロードマップ `1215475353160824` |
| 本番入口 | **チャット**（[`chat-driven-ops.md`](chat-driven-ops.md)）— Asana 自動化・watch 常駐は 100% 必須条件に含めない |

## 目的

「モックは出るが動かない」「fix ループが続く」状態を避け、**依頼者体感の初回完成度を 80% 前後**に揃え、**100% 到達時は Should 全 pass · 本番相当 · polish · SLA** まで明示する SSOT。

## completion_target（プロファイル）

| 値 | 用途 | qa Should 要件 |
|----|------|----------------|
| **80**（既定） | 通常 Epic · M6 節目 | Should **60%+** · 未達は依頼者サマリ明示 |
| **100** | 本番相当 · M8/M9 | Should **100%** · エッジケース · SLA · 本番デプロイ AC |

notes または requirements 先頭: `completion_target: 80` または `completion_target: 100`

## 完成度レベル

| レベル | 定義 | 典型状態 |
|--------|------|----------|
| **~50%** | 見た目・文書・静的 review は通るが、README 手順で起動しない・AC 未検証・代表フロー不通 | モック止まり · fixture fallback · serve 後追い |
| **~80%** | 下記「80% 必須条件」をすべて満たす | 依頼者が README のみで主要機能を確認できる |
| **100%** | 下記「100% 必須条件」をすべて満たす | Should 全 pass · 本番相当 · エッジケース · UX polish · SLA 明示 |

## 80% 必須条件

1. **起動** — README の起動コマンド 1 本で主要画面/API が応答（developer smoke ログ付き）
2. **AC Must** — 要件定義書の Must AC が 100% 充足（qa verification `evidence[]` 付き）
3. **AC Should** — Should AC の 60% 以上充足（未達は依頼者サマリに明示）
4. **代表フロー** — UX Happy path 1 本（5 ステップ以内）が実装で再現
5. **データ経路** — full-ui + bundle 時は **本番 consume 経路**で qa passed（fixture のみ不可）
6. **fix 上限** — 同一ゲート R3 到達時は依頼者エスカレーション（[`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)）

## 100% 必須条件（v2 · M8）

`completion_target: 100` 宣言 Epic のみ適用。

1. **80% 条件の全充足** — 上記 1–6 を満たしたうえで追加要件
2. **AC Should 100%** — 全 Should 行が qa `evidence[]` で pass（[`qa-verifier` SKILL](../skills/development/qa-verifier/SKILL.md) §100%）
3. **本番デプロイ AC** — [`production-deploy-ac-template.md`](production-deploy-ac-template.md) DEP-1–3 Must
4. **エッジケース** — [`edge-case-ac-checklist.md`](edge-case-ac-checklist.md) カテゴリ 3 件以上を AC 化し qa pass
5. **UX polish**（full-ui）— a11y · エラー UI · 空状態（[`ux-reviewer`](../skills/ux/ux-reviewer/SKILL.md) §100% polish）
6. **SLA** — [`production-sla-template.md`](production-sla-template.md) 3 指標を要件に記載し検証記録 1 件
7. **依頼者サマリ** — [`epic-completion-summary-template.md`](epic-completion-summary-template.md) で Should 未達ゼロ · SLA 達成を明示

**含めない（チャット本番）:** org-ops-watch 常駐 · Webhook 無人 kick · 手動 kick 0 件（→ M9 検証はチャットセッション前提に読み替え）

## ゲートとの対応

| フェーズ | 80% 達成に必要な SSOT | 100% 追加 |
|----------|------------------------|-----------|
| 要件 | [`acceptance-criteria-template.md`](acceptance-criteria-template.md) | 本番デプロイ AC · EC · SLA 節 |
| 設計 | tech-designer「実行契約」節 | エッジケース · ロールバック |
| 実装提出 | developer smoke.md | polish 観点メモ |
| code review | smoke 欠落 → failed | EC カテゴリ参照 |
| qa | VerificationResult `evidence[]` Must | **Should 全行** evidence 必須 |
| ux（full-ui） | ux_implementation | polish チェックリスト |
| Epic 完了 | comment_epic_summary | SLA + 100% 達成行 |

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
