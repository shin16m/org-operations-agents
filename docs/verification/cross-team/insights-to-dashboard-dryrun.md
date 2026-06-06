# insights → full-ui ダッシュボード — 継ぎ目 dryrun

実施: 2026-06-06

## 目的

FCB エピックを題材に、**分析 insights 完了 → DashboardBundle → development full-ui consume** のチーム間継ぎ目を記録する。  
組織改善エピック（artifact bridge 強化）の【5/5】検証成果物。

## 契約

| 種別 | パス |
|------|------|
| スキーマ | `schemas/analysis/dashboard-bundle.v1.schema.json` |
| I/O SSOT | `docs/design/insights-dashboard-consume-io.md` |
| bridge | `docs/design/cross-team-artifact-bridge.md` § insights → full-ui |
| 検証 fixture | `docs/verification/fixtures/analysis/dashboard-bundle/fcb-example.v1.json` |

## FCB 参照 Handoff / bootstrap

| 種別 | パス |
|------|------|
| 製品 Handoff | `output/planning/handoff/handoff.fcb-bonding-defect-analysis.json` |
| 組織改善 Handoff | `output/planning/handoff/handoff.org-artifact-bridge-insights.json` |
| bootstrap（FCB intake） | `output/planning/handoff/bootstrap.auto-intake.1215466260354901.json` |

## FCB 分析成果物（提供側）

| 種別 | パス | GID |
|------|------|-----|
| insights | `output/analysis/insights/1215466399377173.md` | `1215466399377173` |
| signatures | `output/analysis/models/1215466399377173-signatures.md` | `1215466532913860` |
| 生データ | `output/analysis/data/fcb-synthetic/chip_quality.csv` | — |
| bundle（想定出力先） | `output/analysis/bundles/1215466399377173-dashboard-bundle.json` | — |

fixture `fcb-example.v1.json` が bundle の参照実装例。

## FCB 開発成果物（消費側 · 現状ギャップ）

| 種別 | パス | ギャップ |
|------|------|----------|
| ダッシュボード | `output/development/app/fcb-dashboard/` | `app.js` に `TOP3` / `SIG_TEMPLATE` 定数コピーあり |
| 開発要件 | `output/development/requirements/*-requirements*.md` | 「CSV のみ・外部 API 不要」で bundle consume と矛盾 |

**改善後の期待:** `assign-plan.insights-dashboard-v1.json` に従い bundle consume + 接続検証サブで再実装。

## 標準 `## 依存（読み取り専用）`（FCB 開発子想定）

```markdown
## 依存（読み取り専用）

| 種別 | 参照 | バージョン | 提供チーム |
|------|------|------------|------------|
| DashboardBundle | `output/analysis/bundles/1215466399377173-dashboard-bundle.json` | v1.0 | analysis |
| 生データ | `output/analysis/data/fcb-synthetic/chip_quality.csv` | v1.0 | analysis |
| UX 仕様 | `output/ux/specs/<ux_child_gid>-ux-spec-v4.md` | v4.0 | ux |

**鮮度 SLA:** UI に `meta.generated_at` と `meta.data_version` を表示すること。
```

## ゲート通過条件

| ゲート | 担当 | 通過条件 |
|--------|------|----------|
| 要件 review | dev-reviewer | bundle consume・定数コピー禁止・鮮度表示が要件に記載 |
| code review | dev-reviewer | `const TOP3` 等の分析値ハードコードなし |
| 動作検証 | qa-verifier | Top3 因子名が bundle と一致、鮮度表示あり |
| 接続検証 | dev-reviewer | known/unknown 件数一致、SIG が bundle `signatures[]` 由来 |
| mismatch | dev-reviewer | 要件 vs as-built で bundle パスが一致 |

## 継ぎ目チェック（組織改善エピック完了時点）

- [x] dashboard-bundle v1 schema 定義（governance 【1/5】）
- [x] insights-dashboard-consume-io.md 作成（governance 【1/5】）
- [x] cross-team-artifact-bridge に insights→full-ui 節（governance 【2/5】）
- [x] development-delivery-io チェックリスト + assign plan 例（governance 【3/5】）
- [x] dev-reviewer / qa-verifier 接続検証観点（governance 【4/5】）
- [ ] FCB ダッシュボードの bundle consume 実装（別 development 子で実施予定）

## 関連

- [`cross-team-artifact-bridge.md`](../../design/cross-team-artifact-bridge.md)
- [`insights-dashboard-consume-io.md`](../../design/insights-dashboard-consume-io.md)
- [`ux-to-dev-full-ui-dryrun.md`](ux-to-dev-full-ui-dryrun.md)
- [`analysis-to-dev-dryrun.md`](analysis-to-dev-dryrun.md)
