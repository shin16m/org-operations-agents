# 分析チーム delivery I/O

workflow: [`workflows/analysis-delivery.yaml`](../../workflows/analysis-delivery.yaml) · 組織: [`department-model.md`](department-model.md)

## 組織

| 項目 | 値 |
|------|-----|
| department id | `analysis` |
| ラベル | 分析チーム |
| PM ハブ | analytics-pm |
| スコープ | Asana 子タスク 1 件 = workflow インスタンス 1 本 |

---

## チーム間 I/O（公式）

### 入力

| 来源 | 形式 |
|------|------|
| task-dispatcher | `DispatchRequest`（`department: analysis`） |
| Asana | 子タスク **notes**（背景・概要・完了条件） |
| Asana（任意） | 親エピック notes |

**読まないもの:** Handoff JSON、PlanReviewResult（チーム間 I/O として禁止）

### 出力

| 形式 | 説明 |
|------|------|
| `DeptWorkComplete` | `department: analysis` |
| Asana | 署名付きコメント + 子タスク完了 |
| チーム内成果物 | 下表 |

---

分析チーム PM 委譲（担当・サブタスク）: [`analytics-pm-assignment.md`](analytics-pm-assignment.md)

---

## チーム内 workflow 概要

```
L2 task-dispatcher（department=analysis）
  → L3 analytics-pm（ハブ）
    → data-architect / data-engineer / data-steward / data-analyst / data-scientist / ml-engineer
    → analysis-reviewer（各ゲート）
  → DeptWorkComplete → 統括グループ
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

## やらないこと

- Handoff 新規作成（→ 企画チーム）
- ディスパッチ（→ task-dispatcher）
- 他チーム成果物の直接編集

---

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
| 分析チームドキュメント・成果物 | `analytics_requirements` \| `data_model` \| `pipeline` \| `data_quality` \| `analysis_insights` \| `model_eval` | `skills/analysis/analysis-reviewer/schemas/analysis-doc-review-result.v1.schema.json` |
| 本番デプロイゲート | `production_deploy_gate` | `skills/analysis/analysis-reviewer/schemas/deploy-gate-result.v1.schema.json` |
| デプロイ検証 | `deploy_verification` | `skills/development/reviewer/schemas/verification-result.v1.schema.json` |

共通: `status` は `passed` \| `passed_with_notes` \| `failed`。

## DeptWorkComplete

analytics-pm 完了時は product-manager と同一スキーマ（`department: analysis`）:

[`skills/development/product-manager/schemas/dept-work-complete.v1.schema.json`](../../skills/development/product-manager/schemas/dept-work-complete.v1.schema.json)

## Asana 記録

開発チームと同様: 各ロール完了時に `comment_task.py`（署名付き）→ analytics-pm が `complete_task.py -y` → `DeptWorkComplete`。

契約: [`agent-asana-comment-signature.md`](agent-asana-comment-signature.md)
