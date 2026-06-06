# WorkflowSession I/O（オーケストレーター入口）

タスク 1 成果物。workflow 段階 ID は [`workflows/default.yaml`](../../workflows/default.yaml) と同一語彙。

## WorkflowSession（セッション状態・草案）

誘導型運用（Cursor 手動起動）で、オーケストレーターが保持・更新する状態。

| フィールド | 型 | 説明 |
|------------|-----|------|
| `session_id` | string | 任意のセッション識別子（例: UUID または日時） |
| `intake_mode` | enum? | `natural_language`（既定）\| `asana_task`。planning gate 分岐の SSOT — **直接チャット**（`natural_language`）は人間承認フロー省略 · **Asana ドリブン**（`asana_task` · watch-auto · auto-intake）は【承認】+ `--record-wait` 必須 |
| `raw_request` | string | 利用者が intake で渡した生課題（自然言語） |
| `source_task_gid` | string? | intake-asana 時の Asana タスク GID |
| `source_task_url` | string? | intake-asana 時の Asana URL |
| `source_task_snapshot_path` | string? | `intake_from_asana.py --out` の JSON パス（v1.1: `comments` / `comments_markdown` 含む場合あり） |
| `current_step_id` | enum | `intake` \| `bootstrap` \| `dispatch` |
| `bootstrap_handoff_path` | string? | bootstrap Handoff JSON のパス |
| `parent_gid` | string? | Asana 親エピック GID |
| `planning_child_gid` | string? | bootstrap 企画子 GID |
| `source_task_closed` | boolean? | intake-asana 時、元タスクを comment+complete 済みか |
| `handoff_path` | string? | 本番 Handoff JSON（企画チーム出力） |
| `review_result_path` | string? | `PlanReviewResult` JSON |
| `workflow_id` | string | 例: `default` |

## SuspendedSession（保留 · Phase 1）

人間 gate（【承認】/【レビュー】）到達時、Cursor セッションを終了する前に **`output/platform/sessions/<session_id>.json`** へ保存する。  
生成 CLI: [`tools/asana_ops_poller.py`](../../tools/asana_ops_poller.py) の `--record-wait`。確認: [`tools/check_workflow_suspend.py`](../../tools/check_workflow_suspend.py)。

| フィールド | 型 | 説明 |
|------------|-----|------|
| `session_id` | string | UTC タイムスタンプ + UUID 短縮 |
| `state` | enum | `suspended`（Phase 1 固定） |
| `gate_kind` | string | 例: `planning_approval` · `pm_review_gate` |
| `marker` | string | 承認サブのプレフィックス（例: `【承認】` · `【レビュー】`） |
| `parent_gid` | string | gate を持つ Asana タスク GID |
| `approval_sub_gid` | string | 承認 / レビューサブ GID |
| `approval_url` | string? | 依頼者が complete する URL |
| `created_at` | string | ISO8601 UTC |

**再開:** `asana_ops_poller --once` が `check_approval_subtask` 経由で complete を検知すると `RESUME` 行を出力。運用者は **新規 dispatch セッション**を起動する（[`asana-driven-ops.md`](asana-driven-ops.md)）。

## orchestrator の役割（v3）

| step id | 役割 | 入力 | 出力（モデル） |
|---------|------|------|----------------|
| `intake` | 課題受付・窓口 | `raw_request` または Asana タスク ref | bootstrap Handoff |
| `bootstrap` | 最小 Asana 作成 | bootstrap Handoff | 親 GID + 企画子 GID |
| `dispatch` | 初回 = 企画チーム配賦 | DispatchRequest | planning-pm 用 prompt_snippet |

企画 gate / Handoff 詳細 / Asana 本番投入は **planning-pm（planning-delivery）** が担当。

## L1 各 step の入出力（default v3）

| step id | agent | 入力 | 出力 |
|---------|-------|------|------|
| `intake` | workflow-orchestrator | 生課題 **または** Asana タスク ref | bootstrap Handoff |
| `bootstrap` | asana-buddy | bootstrap Handoff | Asana 親 + 企画子 |
| `close_intake_source` | asana-buddy | `source_task_gid` + `parent_gid` | 元タスク comment+complete（intake-asana のみ） |
| `dispatch` | task-dispatcher | DispatchRequest（planning） | planning-pm prompt |

## 企画チーム L3（planning-delivery）

| step id | agent | 入力 | 出力 |
|---------|-------|------|------|
| `handoff_plan` | issue-story-planner | 生課題 + 子 notes | `AsanaBuddyHandoff` |
| `plan_review` | plan-reviewer | Handoff 案 | `PlanReviewResult` |
| `pm_gate` | planning-pm | Handoff + Review + `intake_mode` | execute 可否（`natural_language` は同一セッション可 · `asana_task` は【承認】待ち） |
| `asana_execute` | asana-buddy | 承認済み Handoff | Asana タスク群 |
| `pm_complete` | planning-pm | — | `DeptWorkComplete` |

## 拡張

| 段階 | ファイル | 内容 |
|------|----------|------|
| execution 系 dispatch | [`with-dispatch.yaml`](../../workflows/with-dispatch.yaml) | dev / ux / analysis 子 |

## 起動条件

- **intake:** セッション開始時。
- **dispatch（execution 系）:** 企画 `DeptWorkComplete` 後。未完了 execution 系子が存在すること。

生課題 **または Asana タスク URL/GID** で orchestrator（intake / intake-asana）を起動できる。CLI: [`tools/intake_from_asana.py`](../../tools/intake_from_asana.py)（snapshot **v1.1** — notes + ユーザーコメント stories）。**intake-asana** では bootstrap 直後に [`close_intake_source_task.py`](../../skills/platform/asana-buddy/optional/close_intake_source_task.py) で元タスクを新エピックへリンクして complete する。企画・実行の実処理は各チーム workflow に委譲する。

## 移行（v2 → v3）

v2 の `plan` / `review` / `gate` / `execute` は L1 から削除し、planning-delivery（L3）へ移管。履歴: [`docs/verification/cross-team/e2e-dryrun.md`](../verification/cross-team/e2e-dryrun.md)
