# org-ops ↔ org-os プロダクト I/O 契約

| 項目 | 内容 |
|------|------|
| 版 | 2.2 |
| エピック | `1215127084158665` |
| governance 子 | `1215127412682263` |
| 参照 Handoff | `output/planning/handoff/handoff.os-kernelize.json` |

## 1. 目的

**org-os** を epic 状態機械の **カーネル** として分離する。Asana CF が SSOT。org-ops（エージェント・skills）は **syscall / queue API のみ** 経由で epic 状態を読み書きする。

## 2. コンポーネント境界

```
┌─────────────────────────────────────────────────────────────┐
│ org-operations-agents (org-ops)                              │
│  L1: intake → triage → bootstrap → dispatch                 │
│  asana-buddy: handoff_to_asana · create_approval_subtask     │
│  tools: approval_helper · wakuoke_resume_scan · sync CF      │
│  tools/org_os.py  ──────────CLI ラッパー──────────────────┐ │
└─────────────────────────────────────────────────────────────│─┘
                                                              │ syscall / queue
┌─────────────────────────────────────────────────────────────▼─┐
│ products/org-os/ (カーネル)                                    │
│  syscall: start · suspend · resume · complete · init_epic     │
│  queue: ready_queue · wait_list (read-only, FIFO)             │
│  asana_client (CF read/write — 唯一の write path)             │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
                         Asana (SSOT)
```

| 側 | 担う | 担わない |
|----|------|----------|
| **org-ops** | triage · bootstrap · planning dispatch · `.env` GID sync · 承認サブ作成 · @mention | epic CF への直接 PUT（syscall 経由のみ） |
| **org-os** | epic CF read/write · queue 列挙 · 状態遷移 syscall | intake · Handoff · CF フィールド作成 |

## 3. syscall API（write path）

Python: [`products/org-os/src/org_os/syscall.py`](../../products/org-os/src/org_os/syscall.py)

| syscall | 遷移 | 副作用 |
|---------|------|--------|
| `start(epic, agent_id?)` | Ready → Running | suspend reason クリア · Approval Required=No · **ORG_OS_AGENT_ID 必須** |
| `suspend(epic, reason, ref?)` | Ready/Running → Waiting | OS Suspend Reason 設定 · reason=`Approval` 時 Approval Required=Yes |
| `resume(epic, ref?)` | Waiting → Ready | suspend reason クリア · Approval Required=No |
| `complete(epic)` | Ready/Running/Waiting → Done | suspend reason クリア · Approval Required=No |
| `init_epic(epic)` | — | Ready · suspend reason なし · Approval Required=No（bootstrap hook） |

### OS Suspend Reason（Asana enum 表示名）

**snake_case 禁止。** コード定数は Asana UI ラベルと一致:

| 表示名 | 用途 |
|--------|------|
| `Approval` | 【承認】サブ待ち（`create_approval_subtask` → `syscall.suspend(..., "Approval")`） |
| `Human Review` | 人間レビュー待ち |
| `External Block` | 外部依存ブロック |

定数: [`products/org-os/src/org_os/constants.py`](../../products/org-os/src/org_os/constants.py)

## 4. queue API（read-only）

Python: [`products/org-os/src/org_os/queue.py`](../../products/org-os/src/org_os/queue.py)

| API | 内容 |
|-----|------|
| `ready_queue(project)` | Agent Type=AI · Task Type=Epic · OS State=Ready · Approval Required≠Yes · **FIFO（created_at ASC）** |
| `wait_list(project)` | 同上フィルタ · OS State=Waiting · suspend reason 付き |

## 5. Asana カスタムフィールド

### 5.1 フィールド

| フィールド | enum | 用途 |
|-----------|------|------|
| **OS State** | Ready / Running / Waiting / Done | epic 状態機械 |
| **OS Suspend Reason** | Approval / Human Review / External Block | Waiting 時の理由（v2.0 で追加） |
| **Approval Required** | Yes / No | 後方互換 · `Approval` suspend 時に Yes |
| **Approval Result** | OK / NG / 未設定 | 承認サブ完了時に人間が選択 · [`approval-flow.md`](approval-flow.md) |

### 5.2 env キー

sync CLI: [`tools/sync_org_os_cf_env.py`](../../tools/sync_org_os_cf_env.py)

| env キー | 内容 |
|---------|------|
| `ORG_OS_AGENT_ID` | syscall.start のエージェント ID（**未設定時 start はエラー**） |
| `ASANA_OS_STATE_*` | OS State フィールド + enum GID |
| `ASANA_OS_SUSPEND_REASON_*` | OS Suspend Reason フィールド + enum GID |
| `ASANA_APPROVAL_REQUIRED_*` | Approval Required |
| `ASANA_APPROVAL_RESULT_*` | Approval Result（optional） |
| `ASANA_DEFAULT_HUMAN_APPROVER_GID` | 承認サブ assignee + @mention 先 |

テンプレート: [`.env.example`](../../skills/platform/asana-buddy/optional/.env.example)

## 6. org-os CLI 契約

wrapper: [`tools/org_os.py`](../../tools/org_os.py)

| コマンド | 説明 |
|---------|------|
| `org-os status --epic <GID>` | OS State + suspend reason スナップショット |
| `org-os dispatch --epic <GID>` | `syscall.start` エイリアス |
| `org-os complete --epic <GID>` | `syscall.complete` |
| `org-os queue ready\|wait --project <GID> [--json]` | read-only queue |
| `org-os syscall start\|suspend\|resume\|complete ...` | syscall 直叩き |
| `org-os watch --project <GID> [--once]` | ready + wait 一覧ポール |

### 状態遷移

```
Ready --(start)--> Running
Ready/Running --(suspend)--> Waiting  (+ OS Suspend Reason)
Waiting --(resume)--> Ready
Ready/Running/Waiting --(complete)--> Done
```

## 7. org-ops 連携（syscall 化済み）

| ツール | org-os 利用 |
|--------|-------------|
| `handoff_to_asana` / `init_epic_os_state` | `syscall.init_epic` |
| `create_approval_subtask` | `syscall.suspend` on **resolved epic** — 親=epic → `"Approval"` · PM 子等 → epic に `"Human Review"` |
| `approval_helper` | `resolve_epic_gid` → `syscall.resume`（承認完了検知後） |
| `asana_ops_poller --record-wait` | PM 子 GID 時 epic 解決 + `pm_review_gate` で epic `"Human Review"` suspend |
| `wakuoke_resume_scan` | `queue.ready_queue` · READY=`phase=planning` · RESUME OK=`phase=execution` |
| `asana_ops_poller --once` | `PLANNING_DISPATCH`（planning phase READY）または `DISPATCH`（execution RESUME） |
| `complete_epic_os_state` | CLI `org-os complete` |

### 7.1 org-ops 依存マトリクス（§7.1 · C2 · 更新責務）

| ツール / モジュール | syscall | queue | asana_client read | CLI ラッパー | 更新責務 |
|---------------------|---------|-------|-------------------|--------------|----------|
| `tools/org_os.py` | via CLI | via CLI | via CLI | **入口** | platform |
| `tools/complete_epic_os_state.py` | `complete` | — | — | subprocess `org_os.py` | platform |
| `tools/approval_helper.py` | `resume` | — | `resolve_epic_gid` | — | platform |
| `tools/asana_ops_poller.py` | `suspend` · `dispatch`→`start` | `wait_list` | `resolve_epic_gid` | `org_os.py dispatch` | platform |
| `tools/wakuoke_resume_scan.py` | — | `ready_queue` | — | — | platform |
| `tools/asana_ops_dashboard.py` | — | `ready_queue` · `wait_list` | — | — | platform |
| `tools/backfill_epic_os_state.py` | `init_epic` | — | via `backfill.scan` | — | platform |
| `tools/execution_resume_scan.py` | — | `list_project_tasks` | `read_os_state` · `is_watch_epic` | — | platform |
| `tools/execution_kick_guard.py` | — | — | `read_os_state` · `fetch_task` | — | platform |
| `tools/execution_stuck_escalate.py` | — | — | `read_os_state` · `fetch_task` | — | platform |
| `tools/epic_resolve.py` | — | — | `resolve_epic_gid` | — | platform |
| `tools/bypass_planning_gate.py` | `resume` | — | — | — | platform |
| `handoff_to_asana` / `init_epic_os_state` | `init_epic` | — | — | — | asana-buddy |
| `create_approval_subtask` | `suspend` | — | `resolve_epic_gid` | — | asana-buddy |
| `tools/validate_ssot_contract.py` | grep 禁止 | — | — | — | governance |

**境界ルール（CI 検証）:** `tools/*.py`（`org_os.py` 除く）に `set_org_os_custom_fields` · `asana_client.set_os_state` 直叩きがあれば `validate_ssot_contract` が exit 1。

外部利用: [`products/org-os/CONSUMER.md`](../../products/org-os/CONSUMER.md) · リリース: [`RELEASE.md`](../../products/org-os/RELEASE.md)

## 8. 検証

```powershell
python tools/sync_org_os_cf_env.py --project <PROJECT_GID> --write -y
python tools/org_os.py queue ready --project <PROJECT_GID> --json
python tools/org_os.py queue wait --project <PROJECT_GID> --json
python tools/org_os.py watch --project <PROJECT_GID> --once
python tools/validate_ssot_contract.py
python tools/test_org_os_integration.py -v
pytest products/org-os/tests -q
```

## 9. 関連

- approval flow: [`approval-flow.md`](approval-flow.md)
- asana-driven-ops: [`asana-driven-ops.md`](asana-driven-ops.md)
- org-os dryrun: [`../verification/platform/org-os-product-dryrun.md`](../verification/platform/org-os-product-dryrun.md)

## 10. バージョン方針（semver · v1.0.0 凍結）

パッケージ版は [`products/org-os/pyproject.toml`](../../products/org-os/pyproject.toml) · [`CHANGELOG.md`](../../products/org-os/CHANGELOG.md) が SSOT。

| 領域 | 1.0.0 時点の安定 API | 破壊的変更の扱い |
|------|----------------------|------------------|
| **syscall** | `start` · `suspend` · `resume` · `complete` · `init_epic` のシグネチャと遷移表（§3） | MAJOR bump + CHANGELOG + migration 節 |
| **queue** | `ready_queue` · `wait_list` の返却キー（`epic_gid`, `os_state`, `suspend_reason` 等） | フィルタ条件変更は MINOR、キー削除は MAJOR |
| **asana_client read** | `read_os_state` · `is_watch_epic` · `resolve_epic_gid` | 同上 |
| **env 契約** | §5.2 の env キー名 | キー rename は MAJOR（sync CLI 併記） |
| **CLI** | §6 のサブコマンド名 | 削除・改名は MAJOR |

**MINOR** 許容: 後方互換の追加（新 syscall 引数 optional、新 queue キー、doctor チェック追加）。

**PATCH** 許容: バグ修正 · エラーメッセージ改善 · テストのみ。

**org-ops 側:** `tools/org_os.py` はリポジトリ内ラッパー。外部利用は `pip install org-os` 後の `org-os` エントリポイントを正とする（§6）。

**Suspend reason v2.0 注記:** 1.0.0 以降、syscall `suspend(reason=...)` は Asana 表示名のみ受け付ける。旧 snake_case は非対応（0.x からの利用者は CHANGELOG を参照）。
