# 分析チーム delivery I/O

workflow: [`workflows/analysis-delivery.yaml`](../../workflows/analysis-delivery.yaml) v2 · 組織: [`department-model.md`](department-model.md) · 強みの型: [`delivery-strength-pattern.md`](delivery-strength-pattern.md)

## 組織

| 項目 | 値 |
|------|-----|
| department id | `analysis` |
| ラベル | 分析チーム |
| PM ハブ | analytics-pm |
| スコープ | Asana 子タスク 1 件 = workflow インスタンス 1 本 |
| PM 委譲 | [`analytics-pm-assignment.md`](analytics-pm-assignment.md) |

### メンバー（v2）

| slug | slot | 役割 |
|------|------|------|
| analytics-pm | dept_orchestrate | profile・分解・アサイン・完了（**実装・要件の主作成なし**） |
| analytics-requirements-writer | dept_work | 分析要件書 · リリース/KPI レポート |
| data-architect | dept_work | データモデル · SLA |
| data-engineer | dept_work | ETL/ELT パイプライン |
| data-steward | dept_work | 品質 · カタログ · コンプライアンス |
| data-analyst | dept_work | 探索 · BI · インサイト |
| data-scientist | dept_work | モデル開発 · モデルカード |
| ml-engineer | dept_work | デプロイ · 監視（**production_gate 後**） |
| analysis-reviewer | dept_review | 各フェーズ review · 本番ゲート |

---

## delivery profile

| profile | 用途 |
|---------|------|
| **`full`** | 要件 → 本番デプロイまで（既定） |
| **`model-serve`** | 推論 API/モデル — 開発が consume |
| **`insights`** | ダッシュボード・探索のみ |
| **`catalog`** | カタログ · SLA · ガバナンス |
| **`lite`** | 小さなカタログ/ルール更新 |

選定ガイド: [`analytics-pm-assignment.md`](analytics-pm-assignment.md) § profile 選定ガイド

---

## チーム間 I/O（公式）

### 入力

| 来源 | 形式 |
|------|------|
| task-dispatcher | `DispatchRequest`（`department: analysis`） |
| Asana | 子タスク **notes** |
| Asana（任意） | 親エピック notes |

**読まないもの:** Handoff JSON、PlanReviewResult

### 出力

| 形式 | 説明 |
|------|------|
| `DeptWorkComplete` | `department: analysis`, `status`, `summary`, **`artifacts[]`** |
| Asana | `comment_task` → `complete_task` |
| チーム内成果物 | 下表 |

### 下流（開発チーム）向け公開

`model-serve` / `full` で開発がモデル・API を使う場合、完了後に notes へ転記。

テンプレ: [`cross-team-artifact-bridge.md`](cross-team-artifact-bridge.md#分析--開発)

---

## チーム内 workflow（v2 · profile 別）

### full / model-serve（モデル系）

```
analytics-pm（intake・profile）
  → analytics-requirements-writer（requirements）→ analysis-reviewer
  → data-architect → analysis-reviewer（data_model · SLA 必須）
  → data-engineer → analysis-reviewer（pipeline）     # catalog/insights で skip
  → data-steward → analysis-reviewer（data_quality）
  → data-analyst → analysis-reviewer（insights）      # model-serve で skip
  → data-scientist → analysis-reviewer（model_eval）  # insights/catalog で skip
  → analysis-reviewer（production_deploy_gate）       # insights/catalog/lite で skip
  → ml-engineer → analysis-reviewer（deploy_verification）
  → analytics-requirements-writer（release）
  → analytics-pm（DeptWorkComplete）
```

### insights

要件 → 設計 → ETL → 品質 → **探索** → release（モデル・デプロイなし）

### catalog

要件 → 設計 → **品質/カタログ** → release（ETL・探索・モデル・デプロイなし）

---

## 必須ゲート

| ゲート | review_kind | failed 時の修正担当（目安） |
|--------|-------------|---------------------------|
| `requirements_review_passed` | `analytics_requirements` | analytics-requirements-writer |
| `data_model_review_passed` | `data_model` | data-architect |
| `pipeline_review_passed` | `pipeline` | data-engineer |
| `quality_review_passed` | `data_quality` | data-steward |
| `exploration_review_passed` | `analysis_insights` | data-analyst |
| `model_review_passed` | `model_eval` | data-scientist |
| `production_gate_passed` | `production_deploy_gate` | data-scientist / data-steward |
| `deploy_verification_passed` | `deploy_verification` | ml-engineer |

`failed` 時: PM が修正サブ新規 → 再 review（[`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)）。

### SLA（data_model ゲート）

data-architect 成果物に **更新頻度 · 遅延許容 · 可用性 · 鮮度** が無いと `data_model` review は **failed**。

---

## チーム内成果物

| フェーズ | 担当 | 推奨パス |
|----------|------|----------|
| 分析要件 | analytics-requirements-writer | `output/analysis/requirements/<task_gid>-requirements.md` |
| データ設計 | data-architect | `output/analysis/data-model/<task_gid>.md` |
| パイプライン | data-engineer | 別リポジトリ `pipelines/<task_gid>/` |
| カタログ | data-steward | `output/analysis/catalog/<task_gid>.md` |
| インサイト | data-analyst | `output/analysis/insights/<task_gid>.md` |
| モデル | data-scientist | `output/analysis/models/<task_gid>/` |
| デプロイ | ml-engineer | 別リポジトリ `deploy/<task_gid>/` |
| リリース | analytics-requirements-writer | `output/analysis/releases/<task_gid>-release.md` |
| レビュー | analysis-reviewer | `output/analysis/reviews/` |

`DeptWorkComplete.artifacts[]` には下流が参照する **安定 ID**（パス · API URL · バージョン）を列挙する。

---

## 必須運用

| ルール | 内容 |
|--------|------|
| PM 分離 | analytics-pm はワーカー成果物を書かない |
| PM アサイン | profile に応じたサブタスク分解（[`analytics-pm-assignment.md`](analytics-pm-assignment.md)） |
| production_gate | ml-engineer 前に必須（該当 profile のみ） |
| RBAC | data-architect 設計 · data-steward 確認 · 本番データ直接アクセス禁止 |
| 下流 consume | 開発は notes `## 依存` 経由のみ |

---

## やらないこと

- Handoff 新規作成（→ 企画）
- dispatch（→ 統括グループ）
- 他チーム成果物の直接編集

---

## 関連

- PM: [`skills/analysis/analytics-pm/SKILL.md`](../../skills/analysis/analytics-pm/SKILL.md)
- 開発 consume: [`development-delivery-io.md`](development-delivery-io.md)
- bridge: [`cross-team-artifact-bridge.md`](cross-team-artifact-bridge.md)
