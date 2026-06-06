# insights → full-ui ダッシュボード consume I/O

| 版 | 1.0 |
| 日付 | 2026-06-06 |
| スキーマ | [`schemas/analysis/dashboard-bundle.v1.schema.json`](../../schemas/analysis/dashboard-bundle.v1.schema.json) |
| 関連 | [`cross-team-artifact-bridge.md`](cross-team-artifact-bridge.md) · [`analysis-delivery-io.md`](analysis-delivery-io.md) · [`development-delivery-io.md`](development-delivery-io.md) |

## 目的

分析チーム（`profile: insights`）の Markdown 成果物を、開発ダッシュボード（`profile: full-ui`）が **機械可読 JSON** で consume する契約を定義する。  
**JS 定数コピー**（`top_factors`・`conditions`・`signatures` のハードコード）を禁止し、鮮度メタとソース追跡を必須とする。

## 成果物

| 種別 | パス | 提供チーム |
|------|------|------------|
| **DashboardBundle JSON** | `output/analysis/bundles/<analysis_child_gid>-dashboard-bundle.json` | analysis |
| スキーマ | `schemas/analysis/dashboard-bundle.v1.schema.json` | governance |
| 本 I/O doc | `docs/design/insights-dashboard-consume-io.md` | governance |

## DashboardBundle フィールド

| フィールド | 用途（ダッシュボード画面） |
|------------|---------------------------|
| `top_factors[]` | サマリーカード・因子ランキング |
| `conditions[]` | 推奨パラメータレンジ・警戒閾値テーブル |
| `insights.known` / `unknown` | 「わかった／わからない」常設パネル |
| `signatures[]` | 詳細ビュー用の時系列オーバーレイテンプレート |
| `next_actions[]` | ネクストアクション導線 |
| `meta.generated_at` | 鮮度表示（必須 UI 要素） |
| `meta.data_version` | 合成/本番データセット識別 |
| `source_artifacts[]` | 監査・レビュー時の出典追跡 |

## 分析チーム（提供側）

| 順 | 担当 | 操作 |
|----|------|------|
| 1 | data-analyst / data-scientist | insights · charts · signatures 等の Markdown を作成 |
| 2 | analytics-pm またはワーカー | `DashboardBundle` JSON を `output/analysis/bundles/` に出力 |
| 3 | analytics-pm | `DeptWorkComplete.artifacts[]` に bundle パスを含める |

**生成ルール:**

- `top_factors[].impact` は 0–1 の正規化値（ダッシュボードの棒グラフ・順位表示用）
- `signatures[].template_points` は step 軸の代表曲線（10 点程度を推奨）
- `source_artifacts[]` に元 Markdown パスを必ず列挙

## 開発チーム（消費側）

| 順 | 担当 | 操作 |
|----|------|------|
| 1 | product-manager | 分析子完了後、development 子 notes に `## 依存（読み取り専用）` で bundle パスを転記 |
| 2 | developer | `fetch('/data/../bundles/<gid>-dashboard-bundle.json')` 等で読み込み |
| 3 | developer | `top_factors`・`conditions`・`insights`・`signatures` を **bundle から描画**（定数コピー禁止） |
| 4 | developer | UI に `generated_at` / `data_version` を表示 |
| 5 | dev-reviewer / qa-verifier | bundle と画面の因子名・件数一致を検証 |

**禁止:**

- `app.js` 内の分析値ハードコード（bundle フィールドの定数コピー）
- bundle 未参照での分析タブ実装

**許容:**

- CSV 等の生データ読み込み（一覧・マップ表示用）は併用可
- bundle が無い場合はプレースホルダ表示（本番 Handoff では bundle 必須）

## 標準 `## 依存（読み取り専用）`（development 子 notes）

```markdown
## 依存（読み取り専用）

| 種別 | 参照 | バージョン | 提供チーム |
|------|------|------------|------------|
| DashboardBundle | `output/analysis/bundles/<analysis_child_gid>-dashboard-bundle.json` | v1.0 | analysis |
| 生データ | `output/analysis/data/<dataset>/metrics.csv` | v1.0 | analysis |

**利用条件:** 読み取りのみ。契約変更は分析チームの子タスクで依頼する。
**鮮度:** `meta.generated_at` を UI に表示すること。
```

## 鮮度 SLA（推奨）

| 項目 | 推奨 |
|------|------|
| 更新タイミング | 分析子完了時に bundle を再生成 |
| UI 表示 | `generated_at` をローカル日時で表示。「分析データ: {data_version}」を併記 |
|  stale 判定 | 開発側任意。48h 超で警告バッジ等は UX 裁量 |

## 検証

```powershell
python tools/validate_fixture_schemas.py   # dashboard-bundle fixture 含む
```

Fixture 例: [`docs/verification/fixtures/analysis/dashboard-bundle/example.v1.json`](../verification/fixtures/analysis/dashboard-bundle/example.v1.json)

## 参照 assign plan / dryrun

| 種別 | パス |
|------|------|
| 分析 bundle 出力 | `skills/analysis/examples/assign-plan.dashboard-bundle-v1.json` |
| 開発 bundle consume | `skills/development/examples/assign-plan.dashboard-bundle-consume-v1.json` |
| 継ぎ目 dryrun | [`docs/verification/cross-team/insights-to-dashboard-dryrun.md`](../verification/cross-team/insights-to-dashboard-dryrun.md) |
