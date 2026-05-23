# 分析課 I/O・運用ルール

分析課 workflow: [`workflows/analysis-delivery.yaml`](../../workflows/analysis-delivery.yaml) · 組織: [`org-dispatch-model.md`](org-dispatch-model.md)

## レイヤー位置

```
L2 task-dispatcher（department=analysis）
  → L3 analytics-pm（ハブ）
    → data-architect / data-engineer / data-steward / data-analyst / data-scientist / ml-engineer
    → analysis-reviewer（各ゲート）
  → DeptWorkComplete → orchestrator
```

## 成果物パス（推奨・別リポジトリ想定）

| フェーズ | 担当 | 成果物 | 推奨パス例 |
|----------|------|--------|------------|
| 要求定義 | analytics-pm | 要件書・受け入れ基準 | `output/analysis/requirements/<task_gid>.md` |
| データ設計 | data-architect | データモデル・アクセスポリシー | `output/analysis/data-model/<task_gid>.md` |
| 取り込み | data-engineer | パイプラインコード・CI テスト | `pipelines/<task_gid>/` |
| 品質 | data-steward | 品質レポート・データカタログ | `output/analysis/catalog/<task_gid>.md` |
| 探索 | data-analyst | 分析ノート・BI ダッシュボード | `output/analysis/insights/<task_gid>.md` |
| モデル | data-scientist | モデル評価・モデルカード | `output/analysis/models/<task_gid>/` |
| デプロイ | ml-engineer | デプロイ済モデル・監視 | `deploy/<task_gid>/` |
| 価値検証 | analytics-pm | リリースノート・KPI レポート | `output/analysis/releases/<task_gid>.md` |

> 製品コード・パイプライン実体は **別リポジトリ** に置く。本リポジトリは workflow・スキル定義のみ。

## 必須運用ルール

### 1. 契約的 SLA

データ設計（data-architect）成果物に **必ず** 含める:

| 項目 | 説明 |
|------|------|
| 更新頻度 | 例: 日次 06:00 JST、リアルタイム 5 分以内 |
| 遅延許容 | 例: バッチ遅延最大 2 時間、ストリーム lag 最大 10 分 |
| 可用性目標 | 例: 99.5% / 月 |
| データ鮮度 | 例: 参照時点から 24 時間以内 |

`analysis-reviewer`（`review_kind: data_model`）は SLA 未記載を **failed** とする。

### 2. 承認ゲート（本番デプロイ前）

`production_deploy_gate`（analysis-reviewer）は **ml-engineer 着手前に必須**:

- `DeployGateResult.quality_approved: true`
- `DeployGateResult.security_approved: true`
- `DeployGateResult.sla_compliance: true`

いずれか false → `status: failed`。analytics-pm が差し戻し先を判断。

### 3. 監査ログと最小権限

| ルール | 担当 |
|--------|------|
| データアクセスはロールベース（RBAC） | data-architect がポリシー設計、data-steward がコンプライアンス確認 |
| アクセス・変換・デプロイ操作の監査ログ | data-engineer / ml-engineer が実装、data-steward がレビュー |
| 本番データへの直接アクセス禁止（開発は匿名化/サンプル） | 全ロール共通 |

## レビュー結果

| 種別 | review_kind | スキーマ |
|------|-------------|----------|
| 分析課ドキュメント・成果物 | `analytics_requirements` \| `data_model` \| `pipeline` \| `data_quality` \| `analysis_insights` \| `model_eval` | `skills/analysis/analysis-reviewer/schemas/analysis-doc-review-result.v1.schema.json` |
| 本番デプロイゲート | `production_deploy_gate` | `skills/analysis/analysis-reviewer/schemas/deploy-gate-result.v1.schema.json` |
| デプロイ検証 | `deploy_verification` | `skills/development/reviewer/schemas/verification-result.v1.schema.json` |

共通: `status` は `passed` \| `passed_with_notes` \| `failed`。

## DeptWorkComplete

analytics-pm 完了時は product-manager と同一スキーマ（`department: analysis`）:

[`skills/development/product-manager/schemas/dept-work-complete.v1.schema.json`](../../skills/development/product-manager/schemas/dept-work-complete.v1.schema.json)

## Asana 記録

開発課と同様: 各ロール完了時に `comment_task.py`（署名付き）→ analytics-pm が `complete_task.py -y` → `DeptWorkComplete`。

契約: [`agent-asana-comment-signature.md`](agent-asana-comment-signature.md)
