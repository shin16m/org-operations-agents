# workflow-orchestrator SKILL

**独立スキル:** 宣言的 workflow + agent-registry に基づく段階案内。**利用者の唯一の入口（intake）** と **review 後のゲート（gate）** の二役。ビジネスロジックは各スキルに委譲。

人間向け: [`README.md`](README.md) · セッション I/O: [`docs/design/workflow-session-io.md`](../../docs/design/workflow-session-io.md)

## 参照ファイル

| ファイル | 内容 |
|----------|------|
| [`workflows/default.yaml`](../../workflows/default.yaml) | タスク化まで（intake → … → execute） |
| [`workflows/with-execution.yaml`](../../workflows/with-execution.yaml) | 上記 + **work**（単一 task-executor・過渡期） |
| [`workflows/with-dispatch.yaml`](../../workflows/with-dispatch.yaml) | 上記 + **dispatch**（子タスクごと課へ配賦） |
| [`workflows/organizations.yaml`](../../workflows/organizations.yaml) | department → workflow / entry_agent |
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

## registry 未登録 slug

`workflows/default.yaml` が参照する `agent` が [`agent-registry.yaml`](../../workflows/agent-registry.yaml) に無い、または `enabled: false` の場合:

- `execute` / 次段階の案内は**しない**
- `blocked_reason` に slug を明記する
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) の「新エージェント追加」（agent-creater → registry → workflow）を案内する

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
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\handoff_to_asana.py --handoff .\path\to\handoff.json --require-review-result .\path\to\review.json -y --if-not-exists
```

## execute 後の dispatch 委譲（推奨）

Asana 投入後、サブタスク実行依頼を受けたら **子タスク 1 件ごと**に [`task-dispatcher`](../task-dispatcher/SKILL.md) へ。**workflow は [`with-dispatch.yaml`](../../workflows/with-dispatch.yaml)**。

1. `fetch_task.py --gid <parent> --list-subtasks` で未完了子を確認
2. 対象子の `課:` 行または Handoff の `department` を解決
3. dispatcher → 課 workflow（開発課は [`product-manager`](../product-manager/SKILL.md)）

**dispatch 用 prompt_snippet 例:**

```
DispatchRequest（task_gid=〈子GID〉, parent_gid=〈親GID〉, department=development）で
task-dispatcher を起動し、product-manager 用 prompt_snippet を返してください。
```

全子が完了したら利用者へエピック完了を報告する。

### execute / dispatch 後の Asana 完了同期（必須）

課内作業（開発・分析）で **ローカル成果物が `done_when` を満たした時点**で、対応する Asana 子タスクを完了マークする。未完了のままエピック完了報告しない。

| 状況 | コマンド例 |
|------|------------|
| 子 1 件完了 | `comment_task.py` → `complete_task.py --gid <子GID> -y`（**product-manager** が `DeptWorkComplete` の直前に実行） |
| 子【1/N】…【N/N】を一括 | `sync_handoff_epic.py --parent <親GID> --handoff <path> --complete-through N --complete-only` |
| 全子完了後 | 親を `complete_task.py --gid <親GID> -y`（推奨）→ 利用者へエピック完了報告 |

オーケストレーターはセッション終了前に `fetch_task.py --gid <親GID> --list-subtasks` で未完了子が無いか確認する。

## execute 後の work 委譲（過渡期・単一ワーカー）

[`task-executor`](../task-executor/SKILL.md) は **deprecated**。緊急時のみ [`with-execution.yaml`](../../workflows/with-execution.yaml) を使用。

```
指定の Asana サブタスクを task-executor として実行（過渡期）。
```

## 単一窓口について

「単一窓口」は **最初に話しかける相手が orchestrator（intake）** である意味。実行上は intake と gate の **2 回** 起動する。work は execute 後に別依頼または同一セッションで継続。

## 出力形式

- `current_step_id` / `next_agent` / `gate_status`
- `prompt_snippet`
- ブロック時: `blocked_reason` / 戻り先 step
