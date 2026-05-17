# デフォルト E2E 手順（intake → plan → review（必須）→ gate → execute）

workflow 定義: [`workflows/default.yaml`](../../workflows/default.yaml) v2（`policy.review_required: true`, `entry_step: intake`）

## 前提

- リポジトリルートで `.venv` 構築済み（[`skills/asana-buddy/optional/setup_venv.ps1`](../../skills/asana-buddy/optional/setup_venv.ps1)）
- `skills/asana-buddy/optional/.env` に `ASANA_TOKEN`（任意 `ASANA_PROJECT_ID`）

## 0. intake — workflow-orchestrator（ここから開始）

**入力:** 生課題（自然言語）

**プロンプト例:**

```
あなたは workflow-orchestrator スキルです（intake モード）。
課題: 〈依頼内容〉
issue-story-planner への prompt_snippet を返してください。
```

返却されたプロンプトで次の plan を実行する。

## 1. plan — issue-story-planner

**入力:** 課題テーマ（intake から委譲されたプロンプトでも可）

**プロンプト例:**

```
あなたは issue-story-planner スキルです。テーマ「〈課題〉」について課題整理・解決ストーリー・タスク案を出し、
AsanaBuddyHandoff v1.1（各 subtask に background・summary・done_when 必須）の JSON を1つだけ出力してください。
```

**出力:** `handoff.draft.json`

## 2. review — plan-reviewer（必須・省略不可）

**入力:** `handoff.draft.json`

**プロンプト例:**

```
あなたは plan-reviewer スキルです。次の Handoff を PlanReviewResult v1.0 でレビューしてください。
```

**出力:** `review.result.json`、必要なら `handoff.revised.json`

## 3. gate — workflow-orchestrator

**入力:** 改訂 Handoff + PlanReviewResult

**プロンプト例:**

```
あなたは workflow-orchestrator スキルです（gate モード）。
review_passed を確認し、execute（asana-buddy）に進めるか判断してください。
```

## 4. execute — asana-buddy

**入力:** 承認済み Handoff JSON

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\handoff_to_asana.py --handoff .\handoff.revised.json -y --if-not-exists
```

## 移行

以前 planner 先頭で運用していた場合、**新規依頼は step 0（intake）から**。

## 検証記録

- 基盤 11 タスク: [`docs/verification/e2e-dryrun.md`](../verification/e2e-dryrun.md)
- 入口化 5 タスク: [`docs/verification/orchestrator-intake-dryrun.md`](../verification/orchestrator-intake-dryrun.md)
