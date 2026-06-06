# デフォルト E2E 手順（default v3）

workflow 定義: [`workflows/default.yaml`](../../workflows/default.yaml) v3 · 企画チーム: [`workflows/planning-delivery.yaml`](../../workflows/planning-delivery.yaml)

パイプライン概要（SSOT）: [`docs/design/workflow-io-contract.md`](../design/workflow-io-contract.md)

## 前提

- リポジトリルートで `.venv` 構築済み（[`skills/platform/asana-buddy/optional/setup_venv.ps1`](../../skills/platform/asana-buddy/optional/setup_venv.ps1)）
- `skills/platform/asana-buddy/optional/.env` に `ASANA_TOKEN`（任意 `ASANA_PROJECT_ID`）

## 0. intake — workflow-orchestrator（ここから開始）

**入力:** 生課題（自然言語）

**プロンプト例:**

```
あなたは workflow-orchestrator スキルです（intake モード）。
課題: 〈依頼内容〉
bootstrap 用最小 Handoff（親 + department=planning の企画子 1 件）を生成し、
bootstrap → dispatch（企画チーム）まで進めてください。
```

**bootstrap Handoff 要件:**

- 親 `epic.notes_markdown` に生課題全文
- 子 1 件: `title`「企画・Handoff 作成」、`department: planning`
- 各 subtask に `background` / `summary` / `done_when` 必須

**保存例:** `output/planning/handoff/bootstrap.<theme>.json`

## 1. bootstrap — asana-buddy

**入力:** bootstrap Handoff JSON

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\handoff_to_asana.py `
  --handoff .\output\planning\handoff\bootstrap.<theme>.json `
  -y --if-not-exists
```

bootstrap は review 前の最小作成のため **`--require-review-result` は付けない**。

**出力:** 親 GID・企画子 GID をメモする。

## 2. dispatch — task-dispatcher（企画チーム）

**入力:** `DispatchRequest`（`department=planning`）

**プロンプト例:**

```
DispatchRequest: task_gid=<企画子GID>, parent_gid=<親GID>, department=planning
organizations.yaml に従い planning-pm 用 prompt_snippet を返してください。
```

## 3. 企画チーム — planning-pm（planning-delivery）

[`workflows/planning-delivery.yaml`](../../workflows/planning-delivery.yaml) に従い、同一セッションまたは planning-pm セッションで以下を実行する。

### 3a. handoff_plan — issue-story-planner

**プロンプト例:**

```
あなたは issue-story-planner スキルです。テーマ「〈課題〉」について課題整理・解決ストーリー・タスク案を出し、
AsanaBuddyHandoff v1.1 / v1.2（各 subtask に background・summary・done_when 必須）の JSON を1つだけ出力してください。
```

**保存例:** `output/planning/handoff/<theme>.json`

### 3b. plan_review — plan-reviewer（必須・省略不可）

**プロンプト例:**

```
あなたは plan-reviewer スキルです。次の Handoff を PlanReviewResult v1.0 でレビューしてください。
```

**保存例:** `output/planning/plan-review/<theme>.json`

### 3c. pm_gate — planning-pm

**入力:** Handoff + PlanReviewResult

**プロンプト例:**

```
planning-pm（gate モード）として、review_passed を確認し、
Handoff 要約を提示したうえで Asana 投入の承認を待ってください。
```

利用者が **「承認」「Asana に投入して」** と明示するまで `handoff_to_asana.py` を実行しない。

### 3d. asana_execute — asana-buddy

**入力:** 承認済み Handoff JSON + PlanReviewResult

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\handoff_to_asana.py `
  --handoff .\output\planning\handoff\<theme>.json `
  --require-review-result .\output\planning\plan-review\<theme>.json `
  -y --if-not-exists
```

bootstrap で同一 `epic.title` が既にある場合は **新規作成せず sync**（親 notes 更新・execution 系子追加・bootstrap 企画子は fuzzy マッチ）。

`--parent <親GID>` で明示 sync も可。

### 3e. pm_complete — planning-pm

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py `
  --gid <企画子GID> --agent planning-pm --skill skills/planning/planning-pm/SKILL.md `
  --summary "企画完了・Handoff Asana 投入済" --body "..." -y
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\complete_task.py --gid <企画子GID> -y
```

`DeptWorkComplete` を orchestrator へ報告する。

**禁止（同一セッション）:** `asana_execute` 直後に execution 系子（development / ux / analysis）の doc 更新・実装に着手しない。gate 承認は Asana 投入まで。実行系は **§4 task-dispatcher** から開始する（[`workflow-io-contract.md`](../design/workflow-io-contract.md#asana_execute-後execution-系--必須分離)）。

## 4. dispatch — execution 系子（ux / development / analysis）

企画完了（`DeptWorkComplete`）後、**workflow-orchestrator** が未完了 execution 系子を **1 件ずつ task-dispatcher** 経由で配賦する。各 PM は `pm_assign_subtasks` → L3b worker dispatch（[`dispatch-prompt-ssot.md`](../design/dispatch-prompt-ssot.md)）。**PM がワーカー成果物を同一セッションで書かない。**

配賦順: **ux（Web Epic）** → development / analysis（[`dispatch-workflow.md`](dispatch-workflow.md)）。

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <PARENT_GID> --list-subtasks
```

詳細: [`dispatch-workflow.md`](dispatch-workflow.md)

## 移行（v2 → v3）

| v2 | v3 |
|----|-----|
| L1 plan / review / gate / execute | **planning-delivery（L3 企画チーム）** |
| orchestrator gate | **planning-pm gate** |
| intake 後 planner 直接 | intake → bootstrap → dispatch（planning） |

v2 手順の記録: [`docs/verification/archive/`](../verification/archive/README.md)

## 検証記録

- v3 dryrun: [`docs/verification/planning/planning-dept-v3-dryrun.md`](../verification/planning/planning-dept-v3-dryrun.md) · [`all-teams-dryrun.md`](../verification/cross-team/all-teams-dryrun.md)
- v2 履歴: [`docs/verification/archive/default-v2-dryrun.md`](../verification/archive/default-v2-dryrun.md) · [`archive/orchestrator-intake-v2-dryrun.md`](../verification/archive/orchestrator-intake-v2-dryrun.md)
- v3 組織変更: 本ドキュメント · [`docs/design/planning-delivery-io.md`](../design/planning-delivery-io.md)
- PM 代行事後補完: [`docs/verification/platform/asana-comment-detail-delivery.md`](../verification/platform/asana-comment-detail-delivery.md)
