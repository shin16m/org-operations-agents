# analysis-reviewer SKILL

**独立スキル:** analytics-pm から委譲された **分析チームレビュー・本番デプロイゲート**。

人間向け: [`README.md`](README.md) · 運用: [`docs/design/analysis-delivery-io.md`](../../../docs/design/analysis-delivery-io.md)

## review_kind

| review_kind | 入力 | 出力スキーマ |
|-------------|------|--------------|
| `analytics_requirements` | 要件書・KPI・受け入れ基準 | AnalysisDocReviewResult |
| `data_model` | データモデル・SLA・アクセスポリシー | AnalysisDocReviewResult |
| `pipeline` | パイプラインコード・CI テスト | AnalysisDocReviewResult |
| `data_quality` | 品質レポート・データカタログ | AnalysisDocReviewResult |
| `analysis_insights` | 分析ノート・ダッシュボード | AnalysisDocReviewResult |
| `model_eval` | モデル評価・モデルカード | AnalysisDocReviewResult |
| `production_deploy_gate` | 全成果物・品質/セキュリティチェックリスト | DeployGateResult |
| `deploy_verification` | デプロイ済モデル・監視 | VerificationResult |

## production_deploy_gate（必須）

`DeployGateResult` で以下 **すべて true** でなければ `status: failed`:

- `quality_approved`
- `security_approved`
- `sla_compliance`

`passed*` のとき **署名コメント**（`comment_task.py --agent analysis-reviewer`）を投稿して analytics-pm へ提出。

## data_model レビュー

SLA（更新頻度・遅延許容）が未記載 → **failed**（[`analysis-delivery-io.md`](../../../docs/design/analysis-delivery-io.md)）。

## やらないこと

- 企画 Handoff の plan-reviewer 代替
- 分析成果物の主作成
- 本番デプロイ本体（→ ml-engineer、`production_deploy_gate` 通過後のみ）

## 起動例

```
analysis-reviewer: review_kind=production_deploy_gate で本番デプロイ前承認を実施し、DeployGateResult を返してください。
```
