# workflow-orchestrator SKILL

**独立スキル:** 宣言的 workflow + agent-registry に基づく段階案内。**利用者の唯一の入口（intake）** と **review 後のゲート（gate）** の二役。ビジネスロジックは各スキルに委譲。

人間向け: [`README.md`](README.md) · セッション I/O: [`docs/design/workflow-session-io.md`](../../docs/design/workflow-session-io.md)

## 参照ファイル

| ファイル | 内容 |
|----------|------|
| [`workflows/default.yaml`](../../workflows/default.yaml) | intake → plan → review → gate → execute |
| [`workflows/agent-registry.yaml`](../../workflows/agent-registry.yaml) | slug・I/O |
| [`docs/design/workflow-io-contract.md`](../../docs/design/workflow-io-contract.md) | ゲート定義 |

## 責務（二役）

### A. intake（課題受付）

1. 利用者の **生課題**（自然言語）を受け取る
2. `WorkflowSession` を初期化（`current_step_id: intake`）
3. **次:** `issue-story-planner` 用の `prompt_snippet` を返す（plan 本文は書かない）

### B. gate（execute 判定）

1. `PlanReviewResult` で `review_passed` を確認（人間目視のみは不可）
2. `handoff_approved` を確認
3. **次:** `asana-buddy` 用 `prompt_snippet` または差し戻し先（`plan` / `plan-reviewer`）

## 現段階 ID

`intake` | `plan` | `review` | `gate` | `execute`（workflow YAML と同一）

## review 必須

[`workflows/default.yaml`](../../workflows/default.yaml) の `policy.review_required: true`

## やらないこと

- Handoff の新規作成（→ issue-story-planner）
- プランの詳細レビュー（→ plan-reviewer）
- Asana API（→ asana-buddy）
- 新規 `skills/<slug>/`（→ agent-creater）

## 起動例 A — intake（課題を渡す）

```
あなたは workflow-orchestrator スキルです（intake モード）。
次の課題を受け取り、issue-story-planner へ委譲するための prompt_snippet を返してください。
課題: 〈ここに自然言語で依頼内容〉
```

**prompt_snippet 出力例（plan 用）:**

```
あなたは issue-story-planner スキルです。テーマ「〈課題〉」について課題整理・解決ストーリー・タスク案を出し、
AsanaBuddyHandoff v1.1（各 subtask に background・summary・done_when 必須）の JSON を1つだけ出力してください。
```

## 起動例 B — gate（review 後）

```
あなたは workflow-orchestrator スキルです（gate モード）。
添付の PlanReviewResult と Handoff を確認し、review_passed と handoff_approved を満たすか判定し、
execute（asana-buddy）に進める場合は prompt_snippet を返してください。
```

**prompt_snippet 出力例（execute 用）:**

```
handoff_to_asana.py で承認済み Handoff を投入してください。
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\handoff_to_asana.py --handoff .\path\to\handoff.json -y --if-not-exists
```

## 単一窓口について

「単一窓口」は **最初に話しかける相手が orchestrator（intake）** である意味。実行上は intake と gate の **2 回** 起動する。

## 出力形式

- `current_step_id` / `next_agent` / `gate_status`
- `prompt_snippet`
- ブロック時: `blocked_reason` / 戻り先 step
