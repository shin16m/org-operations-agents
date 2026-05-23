# 課内 I/O（DispatchRequest・レビュー結果・完了報告）

エピック: 組織配賦（タスク 4）。企画用 `PlanReviewResult` とは別系統。

## DispatchRequest（task-dispatcher 入力）

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `schema_version` | string | はい | `"1.0"` |
| `task_gid` | string | はい | 子タスク GID |
| `parent_gid` | string | いいえ | 親エピック GID |
| `department` | string | はい | `development` \| `analysis` \| `planning` |
| `workflow_id` | string | いいえ | 省略時は organizations.yaml から解決 |
| `locale` | string | いいえ | 例 `ja-JP` |

スキーマ: [`skills/task-dispatcher/schemas/dispatch-request.v1.schema.json`](../../skills/task-dispatcher/schemas/dispatch-request.v1.schema.json)

## DeptWorkComplete（product-manager → orchestrator）

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `schema_version` | string | はい | `"1.0"` |
| `task_gid` | string | はい | 完了した子タスク |
| `parent_gid` | string | いいえ | 親エピック |
| `department` | string | はい | 例 `development` |
| `status` | enum | はい | `completed` \| `blocked` \| `needs_rework` |
| `summary` | string | はい | 1–2 文 |
| `artifacts` | string[] | いいえ | 成果物パス |

スキーマ: [`skills/product-manager/schemas/dept-work-complete.v1.schema.json`](../../skills/product-manager/schemas/dept-work-complete.v1.schema.json)

### Asana 署名付きコメント（必須）

**どのエージェントが何をしたか**をタスクに残す。設計: [`agent-asana-comment-signature.md`](agent-asana-comment-signature.md)

| タイミング | 担当 | 操作 |
|------------|------|------|
| 委譲作業完了時 | doc-writer / developer / reviewer | `comment_task.py`（`agent` + `skill` + 実施内容） |
| 子タスク完了直前 | **product-manager** | 同上ののち `complete_task.py` |

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\comment_task.py --gid <子GID> --agent developer --skill skills/developer/SKILL.md --summary "..." --body-file .\body.md -y
```

### Asana 完了同期（必須）

**ローカルで `done_when` を満たしても、Asana 上が未完了のままにしない。**

| タイミング | 担当 | 操作 |
|------------|------|------|
| 子タスク 1 件の課内作業完了 | **product-manager** | **`comment_task.py` の後**に `complete_task.py --gid <子GID> -y` を **`DeptWorkComplete` 出力の直前に実行** |
| 同一セッションで複数子を連続完了 | product-manager または orchestrator | `sync_handoff_epic.py --parent <親GID> --handoff <path> --complete-through N --complete-only` |
| 全子完了後 | **workflow-orchestrator** | 親エピックを `complete_task.py --gid <親GID> -y` で完了（任意だが推奨）→ 利用者へエピック完了報告 |

`DeptWorkComplete.status: completed` と Asana の `completed: true` は**セット**で維持する。片方だけ完了は運用エラーとみなす。

## 課内レビュー結果

| 種別 | 用途 | `review_kind` | スキーマ |
|------|------|---------------|----------|
| DocReviewResult | 要件定義 / 詳細仕様 | `requirements` \| `detailed_spec` | `skills/reviewer/schemas/doc-review-result.v1.schema.json` |
| CodeReviewResult | コードレビュー | `code` | `skills/reviewer/schemas/code-review-result.v1.schema.json` |
| VerificationResult | 動作検証 | `verification` | `skills/reviewer/schemas/verification-result.v1.schema.json` |
| MismatchReviewResult | 要件 vs 仕様整合 | `mismatch` | `skills/reviewer/schemas/mismatch-review-result.v1.schema.json` |
| AnalysisDocReviewResult | 分析課ドキュメント | 各種 | `skills/analysis-reviewer/schemas/analysis-doc-review-result.v1.schema.json` |
| DeployGateResult | 本番デプロイ前ゲート | `production_deploy_gate` | `skills/analysis-reviewer/schemas/deploy-gate-result.v1.schema.json` |

分析課の詳細: [`analysis-delivery-io.md`](analysis-delivery-io.md)

共通: `status` は `passed` \| `passed_with_notes` \| `failed`。`failed` 時は差し戻し先を `message` に明記。

### MismatchReviewResult 追加フィールド

| フィールド | 型 | 説明 |
|------------|-----|------|
| `fix_target` | enum | `document` \| `code` |
| `mismatch_summary` | string | 不整合の要約 |

- `document` → doc-writer が仕様書修正
- `code` → PM が developer へ修正依頼（doc-writer 業務は一旦完了）

## TaskWorkRequest との関係（task-executor 移行）

| 項目 | TaskWorkRequest / task-executor | 新モデル |
|------|--------------------------------|----------|
| 単位 | 子 1 件 | 同じ |
| 実行 | 単一エージェントが全部 | dispatcher → 課 workflow → 複数ロール |
| 完了 | TaskWorkResult | DeptWorkComplete |

**移行方針:**

- `task-executor` は **deprecated**（[`with-execution.yaml`](../../workflows/with-execution.yaml) 互換のため registry には残す）。
- 新規依頼は [`with-dispatch.yaml`](../../workflows/with-dispatch.yaml) の `dispatch` + 課 workflow を使う。
- 緊急時のみ「子 GID だけ渡して全部やって」→ task-executor（過渡期）。

## 利用像

```
orchestrator → DispatchRequest → task-dispatcher → product-manager → … → DeptWorkComplete → orchestrator
```
