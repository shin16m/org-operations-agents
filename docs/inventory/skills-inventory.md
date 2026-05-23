# スキル棚卸し（agent-create-supporter）

更新: 企画チーム L3 化（planning-pm ハブ + planning-delivery）後。

設計参照: [`workflows/default.yaml`](../../workflows/default.yaml) · [`workflows/planning-delivery.yaml`](../../workflows/planning-delivery.yaml) · [`workflows/with-dispatch.yaml`](../../workflows/with-dispatch.yaml) · [`workflows/agent-registry.yaml`](../../workflows/agent-registry.yaml)

## 新規エージェント作成の入口

**`agent-creater` のみ**が `skills/<organization>/<slug>/` の設計・雛形を生成する。他スキル・オーケストレーターは新規フォルダを作らない。

## 標準パイプライン（default v3）

```
workflow-orchestrator（intake → bootstrap → dispatch）
  → planning-pm（企画チーム）
    → issue-story-planner → plan-reviewer（必須）→ planning-pm（gate）→ asana-buddy
  → task-dispatcher（execution 系子ごと）
  → product-manager → doc-writer / developer / reviewer（開発チーム）
  → analytics-pm → data-architect / … / analysis-reviewer（分析チーム）
```

- 過渡期: [`workflows/with-execution.yaml`](../../workflows/with-execution.yaml) + `task-executor`
- 組織ルーティング: [`workflows/organizations.yaml`](../../workflows/organizations.yaml)

## スキル一覧

| slug | 種別 | スロット / steps | 状態 | I/O 概要 |
|------|------|------------------|------|----------|
| `workflow-orchestrator` | 業務 | `orchestrate` · intake, bootstrap, dispatch | 実装済 | 生課題 → bootstrap → 企画 dispatch / 実行系 dispatch 委譲 |
| `planning-pm` | 業務 | 企画チームハブ | 実装済 | Handoff → review → gate → Asana → `DeptWorkComplete` |
| `issue-story-planner` | 業務 | `dept_work`（企画チーム） | 実装済 | 課題 → `AsanaBuddyHandoff` v1.1 / v1.2 |
| `plan-reviewer` | 業務 | `dept_review`（企画チーム） | 実装済 | Handoff → `PlanReviewResult` |
| `asana-buddy` | 業務 | `execute` | 実装済 | bootstrap / Handoff → Asana API |
| `task-dispatcher` | 業務 | `dispatch` | 実装済 | `DispatchRequest` → チーム entry 委譲 |
| `product-manager` | 業務 | 開発チームハブ | 実装済 | 子 1 件 → `DeptWorkComplete` |
| `doc-writer` | 業務 | 開発チーム | 実装済 | 要件定義・詳細仕様 |
| `developer` | 業務 | 開発チーム | 実装済 | 実装・修正 |
| `reviewer` | 業務 | 開発チーム | 実装済 | チーム内レビュー・検証 |
| `analytics-pm` | 業務 | 分析チームハブ | 実装済 | 子 1 件 → `DeptWorkComplete` |
| `data-architect` | 業務 | 分析チーム | 実装済 | データモデル・SLA |
| `data-engineer` | 業務 | 分析チーム | 実装済 | ETL/ELT パイプライン |
| `data-steward` | 業務 | 分析チーム | 実装済 | 品質・ガバナンス |
| `data-analyst` | 業務 | 分析チーム | 実装済 | 探索・ダッシュボード |
| `data-scientist` | 業務 | 分析チーム | 実装済 | モデル開発 |
| `ml-engineer` | 業務 | 分析チーム | 実装済 | デプロイ・MLOps |
| `analysis-reviewer` | 業務 | 分析チーム | 実装済 | 分析レビュー・本番ゲート |
| `task-executor` | 業務 | `work` | **deprecated** | 単一ワーカー（過渡期） |
| `agent-creater` | メタ | — | 実装済 | 要件 → `skills/<organization>/<slug>/` 雛形 |

## 機械検証

| 成果物 | スキーマ |
|--------|----------|
| `AsanaBuddyHandoff` v1.1 / v1.2 | `asana-buddy-handoff.v1*.schema.json` |
| `PlanReviewResult` | plan-reviewer schemas |
| `DispatchRequest` / `DeptWorkComplete` | task-dispatcher / product-manager schemas |
| チーム内レビュー（企画） | plan-reviewer schemas |
| チーム内レビュー（開発） | reviewer/schemas/ |
| チーム内レビュー（分析） | analysis-reviewer/schemas/ |

## Handoff 例

| ファイル | 用途 |
|----------|------|
| `handoff.org-dispatch-pm-workflow.json` | 組織配賦・PM ワークフロー |
| `handoff.task-executor-agent.json` | タスク実行フェーズ（レガシー） |
| `handoff.agent-workflow-orchestration.json` | 基盤エピック |
| `handoff.analysis-delivery.json` | 分析チーム delivery |

## レガシー

- `skills/platform/agent-creater/agents/` 配下への配置は**廃止済み**
- default v2（L1 plan/review/gate/execute）: [`docs/verification/e2e-dryrun.md`](../verification/e2e-dryrun.md) に記録
