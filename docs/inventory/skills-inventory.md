# スキル棚卸し（org-operations-agents）

更新: 企画チーム L3 化（planning-pm ハブ + planning-delivery）後。

設計参照: [`workflows/default.yaml`](../../workflows/default.yaml) · [`workflows/planning-delivery.yaml`](../../workflows/planning-delivery.yaml) · [`workflows/with-dispatch.yaml`](../../workflows/with-dispatch.yaml) · [`workflows/agent-registry.yaml`](../../workflows/agent-registry.yaml)

## 新規エージェント作成の入口

**`agent-creater` のみ**が `skills/<organization>/<slug>/` の設計・雛形を生成する。他スキル・オーケストレーターは新規フォルダを作らない。

## 標準パイプライン（default v3）

パイプライン SSOT: [`docs/design/workflow-io-contract.md`](../design/workflow-io-contract.md)

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
| `requirements-writer` | 業務 | 開発チーム | 実装済 | 要件定義・事後仕様 |
| `tech-designer` | 業務 | 開発チーム | 実装済 | 技術設計 |
| `developer` | 業務 | 開発チーム | 実装済 | 実装・修正 |
| `dev-reviewer` | 業務 | 開発チーム | 実装済 | 文書・コード・整合レビュー |
| `qa-verifier` | 業務 | 開発チーム | 実装済 | 動作検証 |
| `ux-pm` | 業務 | UX チームハブ | 実装済 | 子 1 件 → `DeptWorkComplete` |
| `ux-designer` | 業務 | UX チーム | 実装済 | 体験設計・Design System |
| `ux-reviewer` | 業務 | UX チーム | 実装済 | ux_spec / ux_implementation |
| `analytics-pm` | 業務 | 分析チームハブ | 実装済 | 子 1 件 → `DeptWorkComplete` |
| `data-architect` | 業務 | 分析チーム | 実装済 | データモデル・SLA |
| `data-engineer` | 業務 | 分析チーム | 実装済 | ETL/ELT パイプライン |
| `data-steward` | 業務 | 分析チーム | 実装済 | 品質・ガバナンス |
| `data-analyst` | 業務 | 分析チーム | 実装済 | 探索・ダッシュボード |
| `data-scientist` | 業務 | 分析チーム | 実装済 | モデル開発 |
| `ml-engineer` | 業務 | 分析チーム | 実装済 | デプロイ・MLOps |
| `analysis-reviewer` | 業務 | 分析チーム | 実装済 | 分析レビュー・本番ゲート |
| `governance-pm` | 業務 | 組織改善チームハブ | 実装済 | org-meta 子 → `DeptWorkComplete` |
| `ssot-implementer` | 業務 | 組織改善チーム | 実装済 | SSOT ファイル変更 |
| `governance-reviewer` | 業務 | 組織改善チーム | 実装済 | org_meta → `GovernanceReviewResult` |
| `audit-pm` | 業務 | 監査チームハブ | 実装済 | 子 1 件 → `DeptWorkComplete` |
| `consistency-auditor` | 業務 | 監査チーム | 実装済 | 機械検証 → `ConsistencyAuditReport` |
| `audit-reviewer` | 業務 | 監査チーム | 実装済 | org_governance → `AuditReviewResult` |
| `agent-creater` | メタ | — | 実装済 | 要件 → `skills/<organization>/<slug>/` 雛形 |

## 機械検証

| 成果物 | スキーマ |
|--------|----------|
| `AsanaBuddyHandoff` v1.1 / v1.2 | `asana-buddy-handoff.v1*.schema.json` |
| `PlanReviewResult` | plan-reviewer schemas |
| `DispatchRequest` / `DeptWorkComplete` | task-dispatcher / product-manager schemas |
| `UxReviewResult` | ux-reviewer schemas |
| チーム内レビュー（企画） | plan-reviewer schemas |
| チーム内レビュー（開発） | dev-reviewer/schemas/ · qa-verifier/schemas/ |
| チーム内レビュー（UX） | ux-reviewer/schemas/ |
| チーム内レビュー（分析） | analysis-reviewer/schemas/ |
| 監査（機械） | consistency-auditor/schemas/ |
| 監査（レビュー） | audit-reviewer/schemas/ |

## Handoff 例

| ファイル | 用途 |
|----------|------|
| `handoff.org-dispatch-pm-workflow.json` | 組織配賦・PM ワークフロー |
| `handoff.agent-workflow-orchestration.json` | 基盤エピック |
| `handoff.analysis-delivery.json` | 分析チーム delivery |
| `handoff.ux-web-app.json` | UX + full-ui 開発（Web Epic） |
| `handoff.org-governance-audit-team.json` | 監査チーム追加・組織統制 Epic |

## レガシー

- `skills/platform/agent-creater/agents/` 配下への配置は**廃止済み**
- default v2（L1 plan/review/gate/execute）: [`docs/verification/archive/`](../verification/archive/README.md)
