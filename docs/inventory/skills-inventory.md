# スキル棚卸し（agent-create-supporter）

更新: 組織配賦・開発課 PM workflow 追加後。

設計参照: [`workflows/default.yaml`](../../workflows/default.yaml) · [`workflows/with-dispatch.yaml`](../../workflows/with-dispatch.yaml) · [`workflows/agent-registry.yaml`](../../workflows/agent-registry.yaml)

## 新規エージェント作成の入口

**`agent-creater` のみ**が `skills/<slug>/` の設計・雛形を生成する。他スキル・オーケストレーターは新規フォルダを作らない。

## 標準パイプライン（v2 + dispatch）

```
workflow-orchestrator（intake）→ issue-story-planner → plan-reviewer（必須）
  → workflow-orchestrator（gate）→ asana-buddy
  → task-dispatcher（dispatch・子タスクごと）
  → product-manager → doc-writer / developer / reviewer（開発課）
```

- 過渡期: [`workflows/with-execution.yaml`](../../workflows/with-execution.yaml) + `task-executor`
- 組織ルーティング: [`workflows/organizations.yaml`](../../workflows/organizations.yaml)

## スキル一覧

| slug | 種別 | スロット / steps | 状態 | I/O 概要 |
|------|------|------------------|------|----------|
| `workflow-orchestrator` | 業務 | `orchestrate` · intake, gate | 実装済 | 生課題 → plan / Handoff+Review → execute・dispatch 委譲 |
| `issue-story-planner` | 業務 | `plan` | 実装済 | 課題 → `AsanaBuddyHandoff` v1.1 / v1.2 |
| `plan-reviewer` | 業務 | `review` | 実装済 | Handoff → `PlanReviewResult` |
| `asana-buddy` | 業務 | `execute` | 実装済 | Handoff → Asana API |
| `task-dispatcher` | 業務 | `dispatch` | 実装済 | `DispatchRequest` → 課 entry 委譲 |
| `product-manager` | 業務 | 開発課ハブ | 実装済 | 子 1 件 → `DeptWorkComplete` |
| `doc-writer` | 業務 | 開発課 | 実装済 | 要件定義・詳細仕様 |
| `developer` | 業務 | 開発課 | 実装済 | 実装・修正 |
| `reviewer` | 業務 | 開発課 | 実装済 | 課内レビュー・検証 |
| `task-executor` | 業務 | `work` | **deprecated** | 単一ワーカー（過渡期） |
| `agent-creater` | メタ | — | 実装済 | 要件 → `skills/<slug>/` 雛形 |

## 機械検証

| 成果物 | スキーマ |
|--------|----------|
| `AsanaBuddyHandoff` v1.1 / v1.2 | `asana-buddy-handoff.v1*.schema.json` |
| `PlanReviewResult` | plan-reviewer schemas |
| `DispatchRequest` / `DeptWorkComplete` | task-dispatcher / product-manager schemas |
| 課内レビュー | reviewer/schemas/ |

## Handoff 例

| ファイル | 用途 |
|----------|------|
| `handoff.org-dispatch-pm-workflow.json` | 組織配賦・PM ワークフロー |
| `handoff.task-executor-agent.json` | タスク実行フェーズ（レガシー） |
| `handoff.agent-workflow-orchestration.json` | 基盤エピック |

## レガシー

`skills/agent-creater/agents/` 配下への配置は**廃止済み**。
