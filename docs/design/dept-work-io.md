# チーム間共通 I/O（DispatchRequest・DeptWorkComplete）

**チーム間の公式契約**は本書と各チームの `*-delivery-io.md` を参照。**一覧:** [`team-conventions.md`](team-conventions.md) · 全体像: [`department-model.md`](department-model.md)

**Handoff JSON はチーム間 I/O に含めない**（企画チームのチーム内成果物）。

**dispatch prompt SSOT:** [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md) — task-dispatcher が返す起動文の正。

**PM → ワーカー dispatch SSOT:** [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md) — L3b。PM だけが動く状態を防ぐ第 2 配賦。

**レビュー NG → 修正タスク SSOT:** [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md) — Result は PM へ提出。NG 時は修正サブを新規追加。**完了タスクの `--undo` 再開は禁止。**

**新 department 追加時:** [`new-department-checklist.md`](new-department-checklist.md) · 検証: `python tools/validate_org_registry.py`

## DispatchRequest（task-dispatcher 入力）

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `schema_version` | string | はい | `"1.0"` |
| `task_gid` | string | はい | 子タスク GID |
| `parent_gid` | string | いいえ | 親エピック GID |
| `department` | string | はい | `planning` \| `ux` \| `development` \| `analysis` |
| `workflow_id` | string | いいえ | 省略時は organizations.yaml から解決 |
| `locale` | string | いいえ | 例 `ja-JP` |

スキーマ: [`skills/platform/task-dispatcher/schemas/dispatch-request.v1.schema.json`](../../skills/platform/task-dispatcher/schemas/dispatch-request.v1.schema.json)

## DeptWorkComplete（チーム PM → 統括グループ）

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `schema_version` | string | はい | `"1.0"` |
| `task_gid` | string | はい | 完了した子タスク |
| `parent_gid` | string | いいえ | 親エピック |
| `department` | string | はい | `planning` \| `ux` \| `development` \| `analysis` |
| `status` | enum | はい | `completed` \| `blocked` \| `needs_rework` |
| `summary` | string | はい | 1–2 文 |
| `artifacts` | string[] | いいえ | 成果物パス（下流 PM が notes `## 依存` に転記可能 — [`department-model.md`](department-model.md#成果物共有読み取り専用)） |

スキーマ: [`skills/development/product-manager/schemas/dept-work-complete.v1.schema.json`](../../skills/development/product-manager/schemas/dept-work-complete.v1.schema.json)

### Asana 署名付きコメント（必須）

**どのエージェントが何をしたか**をタスクに残す。設計: [`agent-asana-comment-signature.md`](agent-asana-comment-signature.md)（**§4 依頼者向け本文 · §5 ロール別テンプレ**）

| タイミング | 担当 | 操作 |
|------------|------|------|
| 委譲作業完了時 | 各チームワーカー（例: requirements-writer / ux-designer / data-engineer 等） | `comment_task.py`（`agent` + `skill` + **実施内容・成果物・次の状態**） |
| 子タスク完了直前 | **planning-pm / ux-pm / product-manager / analytics-pm** | 同上（**判断・理由**含む）ののち `complete_task.py` |

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py --gid <子GID> --agent ux-designer --skill skills/ux/ux-designer/SKILL.md --summary "..." --body-file .\body.md -y
```

### Asana 完了同期（必須）

**ローカルで `done_when` を満たしても、Asana 上が未完了のままにしない。**

| タイミング | 担当 | 操作 |
|------------|------|------|
| 子タスク 1 件のチーム内作業完了 | **planning-pm / ux-pm / product-manager / analytics-pm** | **`comment_task.py` の後**に `complete_task.py --gid <子GID> -y` を **`DeptWorkComplete` 出力の直前に実行** |
| 同一セッションで複数子を連続完了 | product-manager または orchestrator | `sync_handoff_epic.py --parent <親GID> --handoff <path> --complete-through N --complete-only` |
| 全子完了後 | **workflow-orchestrator** | 親エピックを `complete_task.py --gid <親GID> -y` で完了（任意だが推奨）→ 利用者へエピック完了報告 |

`DeptWorkComplete.status: completed` と Asana の `completed: true` は**セット**で維持する。片方だけ完了は運用エラーとみなす。

## チーム内レビュー結果

| 種別 | 用途 | `review_kind` | スキーマ |
|------|------|---------------|----------|
| DocReviewResult | 要件定義 / 設計 / 詳細仕様 | `requirements` \| `design` \| `detailed_spec` | `skills/development/dev-reviewer/schemas/doc-review-result.v1.schema.json` |
| CodeReviewResult | コードレビュー | `code` | `skills/development/dev-reviewer/schemas/code-review-result.v1.schema.json` |
| VerificationResult | 動作検証 | `verification` | `skills/development/qa-verifier/schemas/verification-result.v1.schema.json` |
| MismatchReviewResult | 要件 vs 仕様整合 | `mismatch` | `skills/development/dev-reviewer/schemas/mismatch-review-result.v1.schema.json` |
| UxReviewResult | UX 仕様 / 実装一致 | `ux_spec` \| `ux_implementation` | `skills/ux/ux-reviewer/schemas/ux-review-result.v1.schema.json` |
| AnalysisDocReviewResult | 分析チームドキュメント | 各種 | `skills/analysis/analysis-reviewer/schemas/analysis-doc-review-result.v1.schema.json` |
| DeployGateResult | 本番デプロイ前ゲート | `production_deploy_gate` | `skills/analysis/analysis-reviewer/schemas/deploy-gate-result.v1.schema.json` |

企画: [`planning-delivery-io.md`](planning-delivery-io.md) · UX: [`ux-delivery-io.md`](ux-delivery-io.md) · 開発: [`development-delivery-io.md`](development-delivery-io.md) · 分析: [`analysis-delivery-io.md`](analysis-delivery-io.md)

共通: `status` は `passed` \| `passed_with_notes` \| `failed`。reviewer は **PM へ提出**（`comment_task` + JSON）。`failed` 時は PM が **修正サブタスクを新規作成**（[`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)）。完了済みタスクを `--undo` しない。

### MismatchReviewResult 追加フィールド

| フィールド | 型 | 説明 |
|------------|-----|------|
| `fix_target` | enum | `document` \| `code` |
| `mismatch_summary` | string | 不整合の要約 |

- `document` → PM が requirements-writer 向け **修正サブ**を新規作成
- `code` → PM が developer 向け **修正サブ**を新規作成

詳細: [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)

## 移行完了（旧 TaskWorkRequest モデル）

旧「単一ワーカーが子 1 件を全部実行」モデル（TaskWorkRequest / TaskWorkResult）は **廃止**。  
現行は **task-dispatcher → チーム PM → ワーカー**（[`department-model.md`](department-model.md)）。

| 旧 | 現行 |
|----|------|
| TaskWorkRequest / TaskWorkResult | `DispatchRequest` / `DeptWorkComplete` |
| 単一 executor | チーム内複数ロール（requirements-writer, developer, …） |

- 新規依頼は [`with-dispatch.yaml`](../../workflows/with-dispatch.yaml) の `dispatch` + チーム workflow を使う。

## 利用像

```
統括グループ → DispatchRequest → task-dispatcher → チーム PM → … → DeptWorkComplete → 統括グループ
```

## 計画と実行の責務境界

| フェーズ | 担当 |
|----------|------|
| 受付 | intake → bootstrap → dispatch（企画） |
| 企画 | planning-delivery（Handoff → review → gate → Asana） |
| 実行 | task-dispatcher → チーム PM → ワーカー（L3b） |

| 責務 | `asana-buddy` | チーム PM + ワーカー |
|------|---------------|----------------------|
| Handoff から親＋子タスク**作成** | はい | いいえ |
| Handoff **新規作成** | いいえ | いいえ（→ issue-story-planner） |
| 既存タスクの **読取** | はい（`fetch_task.py`） | ワーカーが利用 |
| サブタスクの **完了マーク** | はい（`complete_task.py`） | PM / ワーカー完了後 |
| notes の `done_when` に沿った**作業本体** | いいえ | はい（各 worker SKILL） |
| 専用ツール・新規スキルが要る場合 | いいえ | **agent-creater へ委譲** |

- **default v3** の L1 終端は dispatch（企画チームへ初回配賦）。実行は dispatch 後の各 `*-delivery.yaml`。
