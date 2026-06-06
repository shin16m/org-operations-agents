# insights → full-ui ダッシュボード — 継ぎ目 dryrun

実施: 2026-06-06

## 目的

**分析 insights 完了 → DashboardBundle → development full-ui consume** のチーム間継ぎ目を、固定 fixture と assign plan 例で確認する。

## 契約

| 種別 | パス |
|------|------|
| スキーマ | `schemas/analysis/dashboard-bundle.v1.schema.json` |
| I/O SSOT | `docs/design/insights-dashboard-consume-io.md` |
| bridge | `docs/design/cross-team-artifact-bridge.md` § insights → full-ui |
| 検証 fixture | `docs/verification/fixtures/analysis/dashboard-bundle/example.v1.json` |

## fixture / assign plan

| 種別 | パス |
|------|------|
| DashboardBundle 例 | `docs/verification/fixtures/analysis/dashboard-bundle/example.v1.json` |
| 分析 assign plan | `skills/analysis/examples/assign-plan.dashboard-bundle-v1.json` |
| 開発 assign plan | `skills/development/examples/assign-plan.dashboard-bundle-consume-v1.json` |
| 分析 insights（汎用） | `skills/analysis/examples/assign-plan.insights-v2.json` |
| 開発 full-ui（汎用） | `skills/development/examples/assign-plan.full-ui-v1.json` |

## 標準 `## 依存（読み取り専用）`（full-ui + insights 連携）

```markdown
## 依存（読み取り専用）

| 種別 | 参照 | バージョン | 提供チーム |
|------|------|------------|------------|
| DashboardBundle | `output/analysis/bundles/<analysis_child_gid>-dashboard-bundle.json` | v1.0 | analysis |
| 生データ | `output/analysis/data/<dataset>/metrics.csv` | v1.0 | analysis |
| UX 仕様 | `output/ux/specs/<ux_child_gid>-ux-spec.md` | v1.0 | ux |

**鮮度 SLA:** UI に `meta.generated_at` と `meta.data_version` を表示すること。
```

## ゲート通過条件

| ゲート | 担当 | 通過条件 |
|--------|------|----------|
| 要件 review | dev-reviewer | bundle consume・定数コピー禁止・鮮度表示が要件に記載 |
| code review | dev-reviewer | bundle フィールドの JS ハードコードなし |
| 動作検証 | qa-verifier | 上位因子名が bundle と一致、鮮度表示あり |
| 接続検証 | dev-reviewer | known/unknown 件数一致、`signatures[]` が bundle 由来 |
| mismatch | dev-reviewer | 要件 vs as-built で bundle パスが一致 |

## 継ぎ目チェック

- [x] dashboard-bundle v1 schema 定義
- [x] insights-dashboard-consume-io.md 作成
- [x] cross-team-artifact-bridge に insights→full-ui 節
- [x] development-delivery-io チェックリスト + assign plan 例
- [x] dev-reviewer / qa-verifier 接続検証観点
- [x] 汎用 fixture `example.v1.json`（schema 検証対象）

## 関連

- [`cross-team-artifact-bridge.md`](../../design/cross-team-artifact-bridge.md)
- [`insights-dashboard-consume-io.md`](../../design/insights-dashboard-consume-io.md)
- [`analysis-to-dev-dryrun.md`](analysis-to-dev-dryrun.md)
- [`ux-to-dev-full-ui-dryrun.md`](ux-to-dev-full-ui-dryrun.md)
