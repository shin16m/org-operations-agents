# スキル棚卸し（agent-create-supporter）

更新: workflow v2（orchestrator intake 入口）・スキルレビュー是正後。

設計参照: [`workflows/default.yaml`](../../workflows/default.yaml) · [`workflows/agent-registry.yaml`](../../workflows/agent-registry.yaml)

## 新規エージェント作成の入口

**`agent-creater` のみ**が `skills/<slug>/` の設計・雛形を生成する。他スキル・オーケストレーターは新規フォルダを作らない。

## 標準パイプライン（v2）

```
workflow-orchestrator（intake）→ issue-story-planner → plan-reviewer（必須）
  → workflow-orchestrator（gate）→ asana-buddy → task-executor（work・任意）
```

拡張: [`workflows/with-execution.yaml`](../../workflows/with-execution.yaml)

## スキル一覧

| slug | 種別 | スロット / steps | 状態 | I/O 概要 |
|------|------|------------------|------|----------|
| `workflow-orchestrator` | 業務 | `orchestrate` · **intake, gate** | 実装済 | 生課題 → plan 委譲 / Handoff+Review → execute 委譲 |
| `issue-story-planner` | 業務 | `plan` | 実装済 | 課題 → `AsanaBuddyHandoff` v1.1 |
| `plan-reviewer` | 業務 | `review` | 実装済 | Handoff v1.1 → `PlanReviewResult` v1.0 |
| `asana-buddy` | 業務 | `execute` | 実装済 | 承認済み Handoff → Asana API |
| `task-executor` | 業務 | `work` | 実装済 | TaskWorkRequest → 作業 → TaskWorkResult |
| `agent-creater` | メタ | —（workflow 非載せ） | 実装済 | 要件 → `skills/<slug>/` 雛形 |

## 機械検証

| 成果物 | スキーマ |
|--------|----------|
| `AsanaBuddyHandoff` | [`skills/issue-story-planner/schemas/asana-buddy-handoff.v1.schema.json`](../../skills/issue-story-planner/schemas/asana-buddy-handoff.v1.schema.json) |
| `PlanReviewResult` | [`skills/plan-reviewer/schemas/plan-review-result.v1.schema.json`](../../skills/plan-reviewer/schemas/plan-review-result.v1.schema.json) |
| `TaskWorkRequest` / `TaskWorkResult` | [`skills/task-executor/schemas/`](../../skills/task-executor/schemas/) |

Asana 投入: [`handoff_to_asana.py`](../../skills/asana-buddy/optional/handoff_to_asana.py) の `--require-review-result` で review ゲートを CLI 強制可能。

**実行時検証の範囲:** JSON Schema ファイルは契約の単一参照。`load_handoff` / `load_review_result` は必須フィールドと通過 status のみ検証（Handoff と review の同一性照合は未実装）。

## Handoff 例

| ファイル | 用途 |
|----------|------|
| `handoff.example.json` | 汎用例 |
| `handoff.agent-workflow-orchestration.json` | マルチエージェント基盤エピック |
| `handoff.orchestrator-intake-entry.json` | オーケストレーター入口化エピック |
| `handoff.skill-review-remediation.json` | スキルレビュー指摘の是正 |
| `handoff.task-executor-agent.json` | タスク実行フェーズ |

## レガシー

`skills/agent-creater/agents/` 配下への配置は**廃止済み**（削除済み）。正は `skills/<slug>/`。
