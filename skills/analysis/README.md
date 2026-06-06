# analysis — 分析チーム

子タスク 1 件あたり `analysis-delivery` workflow **v2**。analytics-pm がハブ。**profile** でフェーズを出し分ける。

| slug | 役割 |
|------|------|
| analytics-pm | profile · 分解・アサイン・完了（実装・要件の主作成なし） |
| analytics-requirements-writer | 分析要件 · リリース/KPI レポート |
| data-architect | データ設計 · SLA |
| data-engineer | ETL/ELT |
| data-steward | 品質 · カタログ |
| data-analyst | 探索 · BI |
| data-scientist | モデル |
| ml-engineer | デプロイ · 監視 |
| analysis-reviewer | レビュー · 本番ゲート |

## delivery profile

| profile | 用途 |
|---------|------|
| `full` | 要件 → 本番デプロイ（既定） |
| `model-serve` | 推論 API/モデル（開発 consume） |
| `insights` | ダッシュボード・探索 |
| `catalog` | カタログ · SLA |
| `lite` | 小更新 |

assign plan 例: [`examples/assign-plan.model-serve-v2.json`](examples/assign-plan.model-serve-v2.json) · [`assign-plan.insights-v2.json`](examples/assign-plan.insights-v2.json) · [`assign-plan.catalog-v2.json`](examples/assign-plan.catalog-v2.json) · [`assign-plan.dryrun-v2.json`](examples/assign-plan.dryrun-v2.json)

I/O: [`docs/design/analysis-delivery-io.md`](../../docs/design/analysis-delivery-io.md) · PM: [`docs/design/analytics-pm-assignment.md`](../../docs/design/analytics-pm-assignment.md)
