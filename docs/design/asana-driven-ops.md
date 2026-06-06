# Asana ドリブン運用 — org-ops SSOT（Phase 1–3）

| 版 | 1.4 |
| 日付 | 2026-05-26 |
| Phase 1 エピック | `1215101833446108` |
| Phase 2 エピック | `1215087157303128` |
| Phase 3 エピック | `1215087157410286` |
| Phase 4 エピック | `1215087317688245` |
| ブランチ | `feature/asana-driven-ops` |

## 目的

Asana を運用ダッシュボードとして、**AI タスク検出 → intake → 人間承認 → エージェント再開** をチャット依存なく追跡する。Phase 1 は **CLI ポーリング MVP**（Webhook / ダッシュボードは Phase 2+）。

## コンポーネント

| コンポーネント | パス | 役割 |
|----------------|------|------|
| スキャン / ポーラ | [`tools/asana_ops_poller.py`](../../tools/asana_ops_poller.py) | プロジェクト走査 · intake · 保留監視 · **resume scan**（`scan_ready_actions` + `org-os dispatch`）· `--no-scan-resume` で無効化 |
| 保留確認 | [`tools/check_workflow_suspend.py`](../../tools/check_workflow_suspend.py) | suspended 一覧 / gate 状態 · resumable hint |
| RESUME snippet | [`tools/pm_emit_resume_prompt.py`](../../tools/pm_emit_resume_prompt.py) | **Phase 2** — gate complete 後の再開プロンプト |
| sessions 共有 | [`tools/asana_ops_sessions.py`](../../tools/asana_ops_sessions.py) | **Phase 3** — session JSON · webhook ログ |
| Webhook dryrun | [`tools/asana_webhook_handler.py`](../../tools/asana_webhook_handler.py) | **Phase 3** — POST /webhook · complete 検知 |
| ダッシュボード | [`tools/asana_ops_dashboard.py`](../../tools/asana_ops_dashboard.py) | **Phase 3** — WAIT/RESUME 一覧 UI（port 8765） |
| intake snapshot | [`tools/intake_from_asana.py`](../../tools/intake_from_asana.py) | Asana タスク → snapshot JSON |
| 承認サブ作成 | [`create_approval_subtask.py`](../../skills/platform/asana-buddy/optional/create_approval_subtask.py) | 【承認】/【レビュー】汎用（**親 OS State=Waiting / Approval Required=Yes / 人間 assignee も自動設定** — [`approval-flow.md`](approval-flow.md)） |
| 承認 polling | [`check_approval_subtask.py`](../../skills/platform/asana-buddy/optional/check_approval_subtask.py) | サブ complete 検知（1 回） |
| 承認ヘルパー | [`tools/approval_helper.py`](../../tools/approval_helper.py) | 完了監視 + 親 CF 戻し（Ready/No）+ ログ JSON — [`approval-flow.md` §5.1](approval-flow.md) |
| resume scanner | [`tools/wakuoke_resume_scan.py`](../../tools/wakuoke_resume_scan.py) | Ready epic + ヘルパーログを突合し RESUME / ESCALATE 行を出力 · NG ループ上限管理 — [`approval-flow.md` §5.3](approval-flow.md) |

## CLI 出力語彙（UX SSOT）

| 行頭 | 意味 |
|------|------|
| `SCAN` | プロジェクト走査開始 |
| `SKIP` | 候補除外（完了済み · 重複 intake · CF 不一致等） |
| `CANDIDATE` | intake 候補タスク |
| `INTAKE` | snapshot / trigger 実行 |
| `DISPATCH` | RESUME 後 · `phase=execution` · `next=task-dispatcher` 等の execution 再開 hint（**自動 agent kick はしない**） |
| `PLANNING_DISPATCH` | READY · `phase=planning`（approval ログなし = bootstrap 直後等）· **execution DISPATCH 禁止** · `next=planning-pm` |
| `HINT` | `cursor_kick` CLI 提案（`--human` / `--cursor-kick` 時） |
| `KICK` | `CURSOR_API_KEY` + `--cursor-kick -y` で `cursor_epic_dispatch.py` 実行 |
| `START` | `org-os dispatch`（syscall.start）成功 |
| `HINT` | Waiting epic · `approval_helper` 起動提案 |
| `WAIT` | 人間 gate 待ち（**`--record-wait` 保存済み** · ダッシュボード表示） |
| `RESUME` | gate complete / ヘルパーログ突合 — dispatch 再開可 |

## スキャン条件（MVP）

1. `completed = false`
2. CF Agent Type = `AI`（[`asana-assignee-type-field.md`](asana-assignee-type-field.md) · 旧称 担当種別）
3. CF Task Type = `Intake`（[`asana-task-type-field.md`](asana-task-type-field.md)）
4. 同一 `ASANA_PROJECT_ID`（横断は Phase 2）
5. intake 済みでない（source complete または epic リンク story ありは除外）

## 保留 / 再開（Phase 1）

### セッション JSON

保留時、オーケストレーターは [`workflow-session-io.md`](workflow-session-io.md) の **SuspendedSession** を `output/platform/sessions/<session_id>.json` に保存する。

```powershell
python tools/asana_ops_poller.py --record-wait <親GID> <承認サブGID> <承認サブURL>
```

`gate_kind` 例: `planning_approval` · `pm_review_gate`（Phase 2 で拡張）

### 再開検知

```powershell
python tools/asana_ops_poller.py --once          # WAIT / RESUME 行を出力
python tools/check_workflow_suspend.py --list    # 保留一覧
python tools/check_workflow_suspend.py --all --require-resumable  # CI / 手動再開前
```

`RESUME` 検知後、**新規 Cursor セッション**で task-dispatcher / 該当 PM へ dispatch する（同一セッション継続は Phase 2）。

## フロー

### A. 自動 intake（MVP）

```
asana_ops_poller --once
  → CANDIDATE（未完了 · AI · 未 intake）
  → intake_from_asana（--trigger-intake は snapshot のみ · bootstrap は別セッション）
  → bootstrap → plan-review → planning-pm が【承認】サブ作成
  → --record-wait → セッション終了（suspended）
  → 依頼者が【承認】complete
  → poller: RESUME → handoff_to_asana / dispatch 続行
```

### B. PM review gate（既存 · 継続）

[`pm-assign-review-gate.md`](pm-assign-review-gate.md) — `create_pm_review_gate.py` → 【レビュー】complete → L3b dispatch。

planning gate との違い: [`planning-gate-vs-pm-review-gate.md`](planning-gate-vs-pm-review-gate.md)

### C. 手動 intake（維持）

Asana URL/GID をチャットまたは CLI で和久桶に渡す（`intake_mode: asana_task`）。自動スキャンと **併存**。

### 直接チャット intake（人間承認フロー省略）

和久桶さんへ **自然言語で直接依頼**した場合（`intake_mode: natural_language` · workflow-orchestrator 起動例 A）:

- planning gate の【承認】サブ・`--record-wait` は **作らない**
- `PlanReviewResult` 通過後、Handoff 要約提示のうえ **同一セッションで** `handoff_to_asana.py --require-review-result` まで進める

**本節（planning gate Asana 化）は Asana ドリブン intake のみに適用する。**

## planning gate Asana 化（Phase 1 手順 · Asana ドリブン intake 必須）

**Asana ドリブン intake**（intake-asana · watch-auto · `auto_intake_runner` · poller `--auto-bootstrap` · `intake_mode: asana_task`）では、planning gate をチャット「承認待ち」のみで終えてはならない。以下を必須とする（[`workflow-orchestrator/SKILL.md`](../../skills/platform/workflow-orchestrator/SKILL.md) §H · epic `1215131549360577` 実演済）:

1. planning-pm: `PlanReviewResult` 通過後、`create_approval_subtask.py --parent <親エピックGID>` で **【承認】** サブ（notes に Handoff 要約）
   - 親 **`OS State=Waiting`** + **`Approval Required=Yes`** + **`OS Suspend Reason=Approval`**（`syscall.suspend`）
   - サブ assignee = **`ASANA_DEFAULT_HUMAN_APPROVER_GID`**
2. orchestrator / planning-pm: **`--record-wait <親エピックGID> <【承認】サブGID> <URL>`** → SuspendedSession 保存 → **セッション終了**
3. 依頼者: Asana UI で **`Approval Result=OK/NG`** → 【承認】complete
4. 運用者: `approval_helper`（B）→ `wakuoke_resume_scan`（C）→ `RESUME` → `handoff_to_asana.py --require-review-result`

**禁止（Asana ドリブン intake のみ）:** Handoff 要約提示後、**【承認】サブ + `--record-wait` なし**でチャット「承認待ち」のみ。

**直接チャット intake** では上記禁止に該当しない。Asana ドリブンではチャット「承認」「すすめて」は planning gate 到達の代替にならない（RESUME 後の再開合図としては可）。

## 非スコープ（Phase 1）

- ~~マルチプロジェクト横断スキャン~~ → **Phase 2 で実装**（`--projects`）
- ~~Asana Webhook 本番~~ → **Phase 3 で dryrun 実装**（本番 SLA は非スコープ）
- セッション永続化の Cursor ネイティブ統合
- `--trigger-intake` からの完全自動 bootstrap（snapshot + 起動ヒントのみ）

---

## Phase 2 追記（2026-05-24 · エピック `1215087157303128`）

### 追加 CLI

```powershell
# マルチプロジェクト
python tools/asana_ops_poller.py --once --projects 1214771428861230,<OTHER>

# PM review gate 保留
python tools/asana_ops_poller.py --record-wait <親GID> <【レビュー】GID> <URL> \
  --gate-kind pm_review_gate --department development

# RESUME 後 snippet
python tools/pm_emit_resume_prompt.py --list
python tools/pm_emit_resume_prompt.py --session <session_id_prefix>
```

### gate_kind

| gate_kind | marker | record-wait |
|-----------|--------|-------------|
| `planning_approval` | 【承認】 | デフォルト |
| `pm_review_gate` | 【レビュー】 | `--gate-kind pm_review_gate --department <dept>` |

`RESUME` 検知時 `--human` で `pm_emit_resume_prompt` snippet を stderr に出力。

### dryrun

[`asana-driven-ops-phase2-dryrun.md`](../verification/platform/asana-driven-ops-phase2-dryrun.md)

### UX

`output/ux/specs/1215087017928843-ux-spec.md`

---

## Phase 3 追記（2026-05-24 · エピック `1215087157410286`）

### 追加 CLI

```powershell
# Webhook handler（別ターミナル）
python tools/asana_webhook_handler.py --port 8766

# ダッシュボード
python tools/asana_ops_dashboard.py --port 8765

# Webhook テスト POST
curl -X POST http://127.0.0.1:8766/webhook -H "Content-Type: application/json" ^
  -d "{\"events\":[{\"action\":\"changed\",\"resource\":{\"gid\":\"SUB_GID\",\"resource_type\":\"task\"},\"change\":{\"field\":\"completed\",\"new_value\":true}}]}"
```

### poller 併用方針

| 方式 | 用途 |
|------|------|
| **Webhook** | リアルタイム RESUME 検知（優先 · dryrun） |
| **poller** | fallback · マルチプロジェクト SCAN · intake |

両方とも `output/platform/sessions/` を共有。ダッシュボードは `/api/sessions` で一覧表示。

### dryrun

[`asana-driven-ops-phase3-dryrun.md`](../verification/platform/asana-driven-ops-phase3-dryrun.md)

### UX

`output/ux/specs/1215087283197185-ux-spec.md`

---

## Phase 4 追記（2026-05-24 · エピック `1215087317688245`）

### 目的

条件を満たす Asana タスクを検出し、**和久桶さん（workflow-orchestrator）intake** までを段階的に自動化する。**CLI baseline 必須** · **Cursor SDK optional**。

### 検出条件

| # | 条件 | Phase |
|---|------|-------|
| 1 | `completed = false` | 1 |
| 2 | CF Agent Type = `AI` | 1 |
| 3 | CF Task Type = `Intake` | 4 |
| 4 | スキャン対象プロジェクト（`ASANA_PROJECT_ID` または `--projects`） | 2 |
| 5 | 未 intake（`INTAKE_MARKER` story なし） | 1 |

### 二経路

| 経路 | 手段 | 必須 |
|------|------|------|
| **CLI baseline** | `intake_from_asana` → **triage** → bootstrap Handoff → `handoff_to_asana`（review なし）→ planning dispatch | **はい** |
| **CLI 実装** | [`tools/auto_intake_runner.py`](../../tools/auto_intake_runner.py)（triage 統合）· poller `--auto-bootstrap` | 子【2/5】 |
| **org-os** | [`tools/org_os.py`](../../tools/org_os.py) · [`products/org-os/`](../../products/org-os/) | 子【3/5】 · 境界 [`org-os-product-io.md`](org-os-product-io.md) |
| **Cursor SDK** | `Agent.prompt` / `Agent.create` で orchestrator intake-asana プロンプト起動 | optional（PoC 子【3/5】） |

### フロー D. auto-intake（Phase 4）

```
asana_ops_poller --once
  → CANDIDATE
  → INTAKE（snapshot）
  → TRIAGE（epic_input）                    ← v4 追加
  → AUTO_BOOTSTRAP（--auto-bootstrap · 子【2/5】）
  → planning: Handoff · review · gate
  → --record-wait（planning_approval）   ← ダッシュボード WAIT 必須
  → 依頼者【承認】complete
  → RESUME → handoff_to_asana --require-review-result
  → execution dispatch（task-dispatcher → 各 PM）
```

**PM review gate** も `--record-wait --gate-kind pm_review_gate --department <dept>` でダッシュボードに反映する。

### planning gate とダッシュボード

| 段階 | 必須操作 | ダッシュボード |
|------|----------|----------------|
| planning 【承認】作成後 | `asana_ops_poller --record-wait <親> <承認サブ> <URL>` | WAIT 表示 |
| PM 【レビュー】作成後 | `--record-wait ... --gate-kind pm_review_gate --department development` | WAIT 表示 |
| 【承認】/【レビュー】complete | poller `RESUME` · `pm_emit_resume_prompt` | RESUME 表示 |

**注意:** 【承認】/【レビュー】サブ作成だけではダッシュボードに載らない。必ず `--record-wait` で `output/platform/sessions/` に保存する。

**gate 到達時チェックリスト（§H）:** [`workflow-orchestrator/SKILL.md`](../../skills/platform/workflow-orchestrator/SKILL.md) §H — planning gate / PM review gate 到達時の必須手順。

### org-os と人間 gate

| gate | 親 epic org-os | 実装 |
|------|----------------|------|
| planning 【承認】 | `Waiting` + `Approval Required=Yes` | ✅ `create_approval_subtask` → `resolve_epic_gid` → `syscall.suspend(..., Approval)` |
| PM 【レビュー】 | `Waiting` + `Human Review` | ✅ PM 子 GID から親 epic 解決 · `create_approval_subtask` / `--record-wait`（`pm_review_gate`）→ epic `Human Review` · `approval_helper` → `resume` |

詳細: [`planning-gate-vs-pm-review-gate.md`](planning-gate-vs-pm-review-gate.md) §org-os · delivery: [`human-review-suspend-delivery.md`](../verification/platform/human-review-suspend-delivery.md)

### 安全弁

- `--auto-bootstrap` は **dry-run 既定** · `-y` で opt-in
- 重複 intake: 既存 `already_intake_source` / epic リンク story
- CF PUT 400: 警告のみ · 処理継続（[`asana-assignee-type-field.md`](asana-assignee-type-field.md)）
- 手動 intake-asana（チャット URL 渡し）は **併存維持**

### 非スコープ（Phase 4 · SSOT 段階）

- ~~`--auto-bootstrap` / `auto_intake_runner.py` 実装~~ → **実装済**
- ~~Cursor SDK PoC~~ → **実装済** — delivery: [`wakuoke-auto-kick-delivery.md`](../verification/platform/wakuoke-auto-kick-delivery.md)

## Phase 5 追記（2026-06-04 · エピック `1215423734965978`）

### 理想フロー（運用目標 · 2026-06-05 更新）

```
asana_ops_runner --watch
  → auto-bootstrap（Intake 候補）
  → PLANNING_DISPATCH / cursor kick（ORG_OPS_AUTO_KICK + CURSOR_API_KEY）
  → gate（人 · Asana UI）
  → run_cycle 1 回:
       approval_helper_pass → scan_projects(HELPER on RESUME) → resume scan START/DISPATCH
  → session archive
```

**B→C 順序 SSOT:** [`approval-flow.md`](approval-flow.md) §5.2 · epic `1215464614582253` delivery: [`runner-resume-approval-helper-delivery.md`](../verification/platform/runner-resume-approval-helper-delivery.md)

### 追加 CLI

| ツール | 役割 |
|--------|------|
| [`tools/asana_ops_runner.py`](../../tools/asana_ops_runner.py) | watch ループ: bootstrap + helper + resume + archive |
| `ORG_OPS_AUTO_KICK=1` | `CURSOR_API_KEY` あり時、`--cursor-kick` なしで kick 実行 |
| [`asana_ops_sessions.archive_resumable_sessions`](../../tools/asana_ops_sessions.py) | gate complete 済み session → `sessions/archive/` |

```powershell
python tools/asana_ops_runner.py --once --dry-run --human
ORG_OPS_AUTO_KICK=1 python tools/asana_ops_runner.py --watch --interval 60 -y --human
python tools/asana_webhook_handler.py --port 8766   # 本番は reverse proxy 手順: delivery doc
```

### 非スコープ（Phase 5）

- L3b ワーカー無人完走 · `task_dispatcher.py` 自動実行
- Webhook **SLA** · マルチリージョン
- approval_helper 常時デーモン（runner は `--once` パス per cycle のみ）

delivery: [`orchestration-phase5-delivery.md`](../verification/platform/orchestration-phase5-delivery.md)

## Phase 6 追記（2026-06-04 · エピック `1215412762687733`）

### 理想フロー（execution 自動化）

```
asana_ops_runner --watch
  → Phase 5 パス
  → RESUME planning_approval → task_dispatcher.py --kick
  → PM assign → 【レビュー】（人 · 変更なし）
  → RESUME pm_review_gate → cursor_worker_dispatch -y
  → webhook POST → WEBHOOK_SLA latency · /metrics
```

### 追加 CLI

| ツール | 役割 |
|--------|------|
| [`tools/task_dispatcher.py`](../../tools/task_dispatcher.py) | 未完了 execution 子 → dispatch-prompt-ssot 出力 · `--kick -y` |
| [`tools/cursor_worker_dispatch.py`](../../tools/cursor_worker_dispatch.py) | PM review gate 後 L3b SDK kick |
| [`tools/dispatch_prompt_util.py`](../../tools/dispatch_prompt_util.py) | SSOT prompt 読込共有 |
| [`asana_webhook_handler.py`](../../tools/asana_webhook_handler.py) | `/metrics` · `WEBHOOK_SLA` · `--require-secret` |

```powershell
python tools/task_dispatcher.py --parent <EPIC> --list
python tools/task_dispatcher.py --parent <EPIC> --dry-run
ORG_OPS_AUTO_KICK=1 python tools/task_dispatcher.py --parent <EPIC> --kick -y
python tools/cursor_worker_dispatch.py --parent <PM子> --department development --dry-run
python tools/asana_webhook_handler.py --port 8766 --require-secret
curl http://127.0.0.1:8766/metrics
```

### バッチスクリプト（Windows · .cmd）

[`scripts/org-ops/`](../../scripts/org-ops/) — **PowerShell 不要** · venv · `PYTHONIOENCODING` 共通化（[`_common.cmd`](../../scripts/org-ops/_common.cmd)）。

| ファイル | 用途 |
|----------|------|
| [`org-ops-start.cmd`](../../org-ops-start.cmd) | リポジトリ直下 · メニュー起動（ダブルクリック可） |
| `org-ops-once-dryrun.cmd` | 1 サイクル dry-run |
| `org-ops-watch.cmd` | watch（ヒントのみ · `-y` なし） |
| `org-ops-watch-yes.cmd` | 本番 watch（`-y`） |
| `org-ops-watch-auto.cmd` | 本番 + `ORG_OPS_AUTO_KICK=1`（`CURSOR_API_KEY` 未設定時は Python 側 SKIP） |
| `org-ops-webhook.cmd` | Webhook 常駐 |
| `org-ops-dispatch.cmd` | `task_dispatcher`（`list` / `dryrun` / `kick`） |

```cmd
org-ops-start.cmd
scripts\org-ops\org-ops-once-dryrun.cmd
scripts\org-ops\org-ops-watch-yes.cmd
scripts\org-ops\org-ops-dispatch.cmd 1215412762687733 list
scripts\org-ops\org-ops-webhook.cmd --require-secret
```

高度な引数は同ディレクトリの `.ps1` も利用可。

### bootstrap と planning gate（混同防止 · 2026-06-04）

| 段階 | ツール | 作成される Asana | 【承認】 |
|------|--------|------------------|----------|
| L1 bootstrap | `auto_intake_runner` / poller `--auto-bootstrap` | 親 Epic + **企画子 1 件** | **作られない** |
| L3 planning-pm | Handoff → plan-reviewer → `create_approval_subtask` | execution 系子（gate 後） | **ここで初めて作成** |
| watch-auto kick | `PLANNING_DISPATCH` → `cursor_epic_dispatch --mode planning` | （kick 成功時）上記 L3 | kick 成功 + gate 完走時のみ |

**watch-auto で stuck したとき:**

1. poller / runner の **`WARN planning_stuck`** — bootstrap 直後で【承認】が無い正常状態か、kick 失敗かを確認
2. **`KICK stderr`** — Windows ローカル SDK 落ち（`OSError`）時は **手動 planning-pm が正規**
3. Cursor チャット: `planning-pm として子タスク GID <企画子> を進めてください`（poller `--human` の PLANNING_DISPATCH snippet と同じ）

delivery: [`watch-auto-planning-gate-delivery.md`](../verification/planning/watch-auto-planning-gate-delivery.md)

### Windows kick 隔離（WinError 10038 対策 · 2026-06-04）

| 環境変数 | 既定 | 意味 |
|----------|------|------|
| `ORG_OPS_KICK_ISOLATE` | `1` | Windows では `Agent.prompt` を **別 Python 子プロセス**（`cursor_sdk_kick --worker`）で実行 |
| `ORG_OPS_KICK_WORKER` | （内部） | 子プロセス側。再隔離を防ぐ |
| `ORG_OPS_KICK_RUNTIME` | `auto` | `local` · `cloud` · `auto`（`ORG_OPS_REPO_URL` あり時 cloud） |
| `ORG_OPS_REPO_URL` | — | cloud kick 用 git URL（未設定時 `git remote get-url origin`） |
| `ORG_OPS_REPO_REF` | `main` | cloud clone ref |

**共有モジュール:** [`tools/cursor_sdk_kick.py`](../../tools/cursor_sdk_kick.py) — `cursor_epic_dispatch` · `cursor_worker_dispatch` · `cursor_intake_dispatch` · `task_dispatcher` から利用。

**WinError 10038 再発時:**

1. `python tools/cursor_sdk_kick.py --dry-run-isolation` — `enabled=True` か確認
2. `ORG_OPS_KICK_ASYNC=1`（既定 on/win32）で **非同期 SDK** 経由か確認（下記「確定原因と非同期修正」参照）
3. `ORG_OPS_KICK_ISOLATE=0` で in-process に戻す（デバッグのみ）
4. 上記でも失敗 → **手動 planning-pm / dispatch snippet**（watch-auto § と同じ正規ルート）

delivery: [`winerror-10038-kick-fix-delivery.md`](../verification/platform/winerror-10038-kick-fix-delivery.md)

### WinError 10038 確定原因と非同期修正（2026-06-05）

**確定原因（SDK バグ）:** `cursor-sdk 0.1.6` の **同期** bridge（`_bridge._read_discovery`）が、bridge subprocess の stderr **パイプ fd** を `selectors.DefaultSelector()`（Windows では `select()`）で待つ。**Windows の `select()` はソケット専用**でパイプ不可 → `OSError WinError 10038`。隔離・UTF-8 化・cloud 切替では直らない（bridge 起動は runtime 判定より前）。

**修正:** `cursor_sdk_kick._kick_in_process` は Windows で **非同期 SDK**（`AsyncClient.launch_bridge` + `AsyncAgent.prompt`）を使う。Windows の asyncio は **ProactorEventLoop（IOCP/overlapped IO）** でパイプを読むため `select()` を経由せず 10038 を回避。

| 環境変数 | 既定 | 意味 |
|----------|------|------|
| `ORG_OPS_KICK_ASYNC` | `1`（win32）/ `0`（他） | `1`=非同期 SDK 経由（10038 回避）。`0`=従来の同期 `Agent.prompt` |

**実機検証:** 同期 `Bridge.launch(workspace='.')` → `WinError 10038`。非同期 `AsyncClient.launch_bridge(workspace='.')` → bridge 正常起動（`http://127.0.0.1:PORT`）。回帰: `test_cursor_sdk_kick.py::test_kick_in_process_uses_async_on_win32`。

これにより **local kick がそのまま成功**し、planning【承認】が自動作成される。cloud フォールバックは安全網として残すが、通常運用では不要。

### Windows 文字コード（隔離 kick · UnicodeDecodeError · 2026-06-04）

| 層 | 対策 |
|----|------|
| `.cmd` / `_common.cmd` | `PYTHONIOENCODING=utf-8` |
| `cursor_sdk_kick --worker` | 子 stdout/stderr を UTF-8 に `reconfigure` |
| 隔離 kick **親** | `subprocess.run(..., encoding=utf-8, errors=replace)` + 子 env に `PYTHONIOENCODING=utf-8` |
| poller / runner | `_run_capture` 同等（既存） |

**UnicodeDecodeError（cp932）再発時:** 隔離 kick 親の `subprocess.run` に `encoding` 未指定が典型。`tools/test_cursor_sdk_kick.py` の `test_isolated_subprocess_uses_utf8_decode` で回帰確認。

delivery: [`kick-subprocess-unicode-delivery.md`](../verification/platform/kick-subprocess-unicode-delivery.md)

### local bridge 不可環境の正規運用（cloud kick · 2026-06-04）

**前提:** WinError 10038 の確定原因は同期 bridge の `select()`（上記「確定原因と非同期修正」）。**非同期化（`ORG_OPS_KICK_ASYNC=1`、既定）で local kick は成功する**ため、通常はこのセクションの cloud フォールバックは不要。以下は API key 不在や repo 未 clone など local 不可な残ケースの安全網。

| ルート | 条件 | 動作 |
|--------|------|------|
| local kick | 既定（bridge 正常時） | 隔離 subprocess で `Agent.prompt` |
| **cloud フォールバック** | local 失敗 + `ORG_OPS_KICK_FALLBACK_CLOUD`（既定 on/win32）+ repo URL 解決可 | **1 回 cloud runtime でリトライ**（`cursor_sdk_kick`） |
| 手動 planning-pm | cloud も不可 / API key なし | poller `--human` の PLANNING_DISPATCH snippet を Cursor へ貼付 |

**cloud kick の前提（重要）:**

- cloud runtime は **push 済みブランチを clone** する。**未コミット/未 push の変更は反映されない。**
- `ORG_OPS_REPO_URL`（未設定時 `git remote get-url origin`）と `ORG_OPS_REPO_REF`（既定 `main`）が必要。
- 運用前に対象ブランチを push しておくこと。

**stuck 検知:** bootstrap のみで【承認】が無い epic は poller/runner が毎サイクル `WARN planning_stuck` を再出力する。**承認到達まで epic を Done 化しない。** 承認未作成が続く場合は cloud kick 設定または手動 planning-pm へ切替える。

delivery: [`auto-kick-approval-not-created-delivery.md`](../verification/platform/auto-kick-approval-not-created-delivery.md)

### planning 承認後の execution 子 materialize（auto-kick 経路 · 2026-06-05）

**症状:** planning【承認】complete → RESUME 後、auto-kick が `task_dispatcher` を直叩きして `DISPATCH no target` を返し前に進まない。

**原因:** execution 系子は **承認後に `handoff_to_asana` が作る**。RESUME 時点ではまだ存在しないのに、`asana_ops_poller._cursor_kick_hint` が `gate=planning_approval` の RESUME を `else → task_dispatcher --kick` に流していた（材料となる execution 子が無いため `no target`）。

**修正:** `_cursor_kick_hint` に `gate=="planning_approval"` 分岐を追加し、`cursor_epic_dispatch.py --mode execution --gate-kind planning_approval` を kick する。これは workflow-orchestrator agent を起動し **(1) Handoff 特定 → handoff_to_asana `--if-not-exists` で execution 子作成 → (2) task_dispatcher** を実行する。回帰: `test_planning_stuck.py::CursorKickRoutingTests`。

**既に stuck した epic（session archive 済）の手動 unblock:**

```powershell
python tools/approval_helper.py --parent <wait_target> --approval-sub <gate_sub> --gate-kind planning_approval --once
python tools/asana_ops_runner.py --once -y --cursor-kick
```

`wait_target` は planning gate では **親 epic GID** · PM review gate では **PM 子 GID**（`approval_helper` が epic を resume）。

### gate complete 後 stuck（helper 未実行 · execution 前走り · 2026-06-05）

**症状:** planning 【承認】/ PM 【レビュー】を UI complete したが epic が **Waiting** のまま · `ready_queue=0` · 開発 PM 子だけ先に動いている。

**主因:** runner 1 サイクル内で `approval_helper` が走らない B→C gap（[`runner-resume-approval-helper-delivery.md`](../verification/platform/runner-resume-approval-helper-delivery.md)）。

**副因:** epic `os_state != Running` または企画子未 complete 中に `task_dispatcher` / `cursor_worker_dispatch` / `execution_resume_scan` が kick する。

**コードガード（`tools/execution_kick_guard.py`）:**

| 条件 | 動作 |
|------|------|
| epic `os_state != Running` | `BLOCKED execution_kick epic=<gid> reason=epic_state=Waiting` |
| 企画子（`department=planning`）未 complete | `BLOCKED … reason=planning_child_open=<gid>` |
| 上記 OK | kick 継続 |

**手動 unblock（1 行 + runner）:**

```powershell
python tools/approval_helper.py --parent <wait_target> --approval-sub <gate_sub> --gate-kind <planning_approval|pm_review_gate> --once
python tools/asana_ops_runner.py --once -y --cursor-kick
```

**watch-auto コード更新後:** プロセス再起動必須（`org-ops-watch-auto.cmd`）。

delivery: [`watch-auto-stuck-unblock-delivery.md`](../verification/platform/watch-auto-stuck-unblock-delivery.md)

**既に stuck した epic（session archive 済）の execution materialize 手動:**

```powershell
python tools/cursor_epic_dispatch.py --epic <EPIC_GID> --mode execution --gate-kind planning_approval -y
```

### 非スコープ（Phase 6）

- PM / planning 人間 gate 自動 complete
- ワーカー成果物の無人 epic 完走
- Webhook 常駐を runner に内包

delivery: [`orchestration-phase6-delivery.md`](../verification/platform/orchestration-phase6-delivery.md)

## Phase 7 — Running epic L3b チェーン（2026-06-05 · エピック `1215436815983476`）

Phase 5「L3b 非スコープ」を **Running epic scan + PM bridge** で解消。人間 gate（planning 【承認】· PM 【レビュー】）は維持。

### 理想フロー（execution L3b 自動化）

```
asana_ops_runner --watch  (ORG_OPS_AUTO_KICK=1)
  → Phase 5–6 パス（intake · planning RESUME · pm_review_gate RESUME）
  → EXECUTION_SCAN（OS State=Running epic）
      needs_pm_kick      → task_dispatcher --kick -y
      wait_pm_review     → WAIT（人 · Asana UI）
      needs_worker_kick  → cursor_worker_dispatch -y
      needs_pm_complete  → pm_worker_complete_bridge -y
      idle               → 出力のみ
  → 次 execution 子（governance / audit）も needs_pm_kick 経路
```

**`ready_total=0` でも Running epic を scan する**（Phase 5 の ready_queue 限定を補完）。

### 追加 CLI

| ツール | 役割 |
|--------|------|
| [`tools/execution_resume_scan.py`](../../tools/execution_resume_scan.py) | Running epic · 状態機械 · `EXECUTION_SCAN` 行 |
| [`tools/pm_worker_complete_bridge.py`](../../tools/pm_worker_complete_bridge.py) | worker 署名 comment 後の PM `complete_task` kick |
| [`tools/cursor_epic_dispatch.py`](../../tools/cursor_epic_dispatch.py) | Phase A: execution prompt step 3 に `--kick -y` |

### 環境変数

| 変数 | 既定 | 意味 |
|------|------|------|
| `ORG_OPS_MAX_WORKER_KICKS_PER_CYCLE` | `1` | runner 1 サイクルあたり execution kick 上限 |

### 状態表（SSOT）

| state | 検知 | auto-kick |
|-------|------|-----------|
| `needs_pm_kick` | execution 子あり · PM 子下 worker サブ 0 | `task_dispatcher --kick -y` |
| `wait_pm_review` | 【レビュー】未 complete | WAIT + approval_helper（既存） |
| `needs_worker_kick` | review complete · worker 未 comment | `cursor_worker_dispatch -y` |
| `needs_pm_complete` | worker 署名 comment 済 · 未 complete | `pm_worker_complete_bridge -y` |
| `idle` | 人間 gate / 全 execution 子 complete | なし |

`needs_next_dept`（次 execution 子）は **`needs_pm_kick` と同一 dispatcher 経路**（`pick_target` が次 dept 子を選ぶ）。

### 非スコープ（Phase 7）

- 【承認】/【レビュー】の agent complete
- L3b 成果物の無人 merge
- 和久桶による L3 実装作業

delivery: [`watch-auto-l3b-execution-chain-delivery.md`](../verification/platform/watch-auto-l3b-execution-chain-delivery.md)

### CLI（Phase 4 legacy）

```powershell
python tools/auto_intake_runner.py --task <SOURCE_GID> --dry-run
python tools/auto_intake_runner.py --task <SOURCE_GID> -y
python tools/asana_ops_poller.py --once --auto-bootstrap --dry-run
python tools/asana_ops_poller.py --once --auto-bootstrap -y
```

### dryrun（予定）

[`asana-driven-auto-intake-dryrun.md`](../verification/platform/asana-driven-auto-intake-dryrun.md)（子【5/5】）

## 参照

- UX: `output/ux/specs/1215086510974424-ux-spec.md`
- development dryrun: [`asana-driven-ops-dryrun.md`](../verification/platform/asana-driven-ops-dryrun.md)
- Agent Type CF: [`asana-assignee-type-field.md`](asana-assignee-type-field.md)
