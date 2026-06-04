# org-ops ↔ org-os プロダクト I/O 契約

| 項目 | 内容 |
|------|------|
| 版 | 2.0 |
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

## 8. 検証

```powershell
python tools/sync_org_os_cf_env.py --project <PROJECT_GID> --write -y
python tools/org_os.py queue ready --project <PROJECT_GID> --json
python tools/org_os.py queue wait --project <PROJECT_GID> --json
python tools/org_os.py watch --project <PROJECT_GID> --once
python tools/validate_ssot_contract.py
```

## 9. 関連

- approval flow: [`approval-flow.md`](approval-flow.md)
- asana-driven-ops: [`asana-driven-ops.md`](asana-driven-ops.md)
- org-os dryrun: [`../verification/org-os-product-dryrun.md`](../verification/org-os-product-dryrun.md)
