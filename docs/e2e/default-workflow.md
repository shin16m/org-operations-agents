# デフォルト E2E 手順（plan → review（必須）→ orchestrate → execute）

workflow 定義: [`workflows/default.yaml`](../../workflows/default.yaml)（`policy.review_required: true`）

## 前提

- リポジトリルートで `.venv` 構築済み（[`skills/asana-buddy/optional/setup_venv.ps1`](../../skills/asana-buddy/optional/setup_venv.ps1)）
- `skills/asana-buddy/optional/.env` に `ASANA_TOKEN`（任意 `ASANA_PROJECT_ID`）

## 1. plan — issue-story-planner

**入力:** 課題テーマ（自然言語）

**プロンプト例:**

```
あなたは issue-story-planner スキルです。テーマ「〈課題〉」について課題整理・解決ストーリー・タスク案を出し、
AsanaBuddyHandoff v1.1（各 subtask に background・summary・done_when 必須）の JSON を1つだけ出力してください。
```

**出力ファイル例:** `handoff.draft.json`（ユーザーが保存）

## 2. review — plan-reviewer（必須・省略不可）

**入力:** `handoff.draft.json`

**プロンプト例:**

```
あなたは plan-reviewer スキルです。次の Handoff を PlanReviewResult v1.0 でレビューしてください。
```

**出力:** `review.result.json`、必要なら `handoff.revised.json`

## 3. orchestrate — workflow-orchestrator

**入力:** 改訂 Handoff + PlanReviewResult

**プロンプト例:**

```
あなたは workflow-orchestrator スキルです。review_passed を確認し、execute（asana-buddy）に進めるか判断してください。
```

## 4. execute — asana-buddy

**入力:** 承認済み Handoff JSON

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\handoff_to_asana.py --handoff .\handoff.revised.json -y --if-not-exists
```

## ワークフロー拡張例（スモーク）

1. `workflows/agent-registry.yaml` に `slug: example-dummy`（`enabled: false` 可）を追加
2. `workflows/default.yaml` に段階を1つ挿入する案を PR で検討（本番は orchestrator が未登録 slug でエラーを返すことを確認）

詳細検証記録: [`docs/verification/e2e-dryrun.md`](../verification/e2e-dryrun.md)
