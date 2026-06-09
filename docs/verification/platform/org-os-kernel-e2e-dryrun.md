# org-os カーネル E2E 再検証（syscall + OS Suspend Reason）

> **履歴（RETIRED · 2026-06-09）** — Asana **自動化** / org-os の検証記録。本番は [chat-driven-ops.md](../../design/chat-driven-ops.md)（和久桶チャット入口 · Asana タスク運用継続）。


| 項目 | 値 |
|------|------|
| 実施日 | 2026-05-26 |
| プロジェクト | `1214771428861230`（本番） |
| 親 epic | `1215128751110604` |
| 企画子 | `1215127986198705` |
| 承認サブ | `1215128496651077` |
| 承認担当者 | `1214766054680419`（murata1328@gmail.com） |
| profile | doc-only（検証用エピック · 実装変更なし） |

## 目的

カーネル化（`c97b600`）後の承認フロー A+B+C を **syscall 経由**で再実行し、以下を確認する:

1. `create_approval_subtask` → `syscall.suspend(..., "Approval")` + `@mention`
2. `approval_helper` → `syscall.resume`
3. `wakuoke_resume_scan` → `queue.ready_queue` + `RESUME` 行

前回 E2E（[`approval-flow-e2e-dryrun.md`](approval-flow-e2e-dryrun.md)）は **CF 直書き** 前提。本記録は **OS Suspend Reason CF** 込みの回帰テスト。

## 事前準備

| 作業 | 完了 |
|------|------|
| `OS Suspend Reason` CF（Approval / Human Review / External Block） | ✅ 依頼者 |
| `sync_org_os_cf_env.py --write` + `ORG_OS_AGENT_ID` | ✅ |
| 本番 `.env`（project `1214771428861230`） | ✅ |

## 実施ステップと結果

### 0. bootstrap（検証用 epic 作成）

```powershell
python skills/platform/asana-buddy/optional/handoff_to_asana.py `
  --handoff docs/verification/fixtures/planning/handoff/bootstrap.kernel-e2e.json -y
```

| 項目 | 結果 |
|------|------|
| 親 epic 作成 | ✅ `1215128751110604` |
| Task Type=Epic · OS State=Ready · Approval Required=No | ✅ `init_epic_os_state` |
| 企画子 | ✅ `1215127986198705` |

### 1. **A — create_approval_subtask（syscall.suspend）** ✅

**根本原因（メンション无效）:** 初回実装は (1) plain `text` + `<@gid>`、(2) 修正版は `html_text` 内に **非許可タグ `<br/>`** を使用。Asana は HTML をエスケープして平文表示し、@-mention も通知も発火しない。

**検証済みの正しい形式（story `1215129582927755`）:** 許可タグのみ + `data-asana-type="user"` → API 応答で `@ichiro` リンクに展開される。

```powershell
python skills/platform/asana-buddy/optional/create_approval_subtask.py `
  --parent 1215128751110604 `
  --title "【承認】kernel E2E — syscall suspend/resume 検証" -y
```

実行ログ:

```
assigned_human 1215128496651077 1214766054680419
parent_syscall_suspend 1215128751110604 os_state=Waiting reason=Approval
mention_posted sub=1215128496651077 user=1214766054680419
created_approval_subtask 1215128496651077
```

**org-os status（親）:**

```json
{
  "os_state": "Waiting",
  "approval_required": "Yes",
  "suspend_reason": "Approval"
}
```

**wait_list:**

```json
[{
  "epic_gid": "1215128751110604",
  "os_state": "Waiting",
  "suspend_reason": "Approval"
}]
```

| 項目 | 旧 E2E | 本 E2E |
|------|--------|--------|
| 親 Waiting | ✅ | ✅ |
| Approval Required=Yes | ✅ | ✅ |
| **OS Suspend Reason=Approval** | —（未検証） | ✅ |
| **@mention（html_text · 許可タグのみ）** | — | ✅ story `1215129582927755` で `@ichiro` 展開確認 |
| **担当者通知** | — | ⚠️ PAT ユーザー = 承認者 GID（同一 `1214766054680419`）のため自己 mention は通知されない想定 |
| 人間 assignee | ✅ | ✅ |

### 2. **人間操作** — Asana UI で承認 ✅

依頼者が Approval Result=OK を選択しサブ complete（2026-05-26）。

### 3. **B — approval_helper（syscall.resume）** ✅

```
APPROVED sub=1215128496651077 result=OK
```

**org-os status（親）:**

```json
{
  "os_state": "Ready",
  "approval_required": "No",
  "suspend_reason": null
}
```

ログ JSON（`suspend_reason: null` 含む）: `output/platform/approval-helper/1215128751110604-1215128496651077.json`

### 4. **C — wakuoke_resume_scan** ✅

```
SCAN  project=1214771428861230  max_ng=3  dry_run=True
RESUME parent=1215128751110604  result=OK  next=execution_dispatch
DONE  ready_total=1
```

ヘルパーログ `consumed: true` 更新済み。

### 5. 後片付け（任意）

検証 epic を残す場合はそのまま。不要なら:

```powershell
python tools/org_os.py complete --epic 1215128751110604
python skills/platform/asana-buddy/optional/complete_task.py --gid 1215128751110604 -y
```

## 結論

カーネル化後の A+B+C は本番プロジェクト `1214771428861230` で **syscall 経由**の end-to-end 動作を確認した。

| Phase | 状態 |
|-------|------|
| A（syscall.suspend + OS Suspend Reason + html_text mention） | ✅ |
| 人間承認 | ✅ |
| B（syscall.resume · suspend_reason クリア） | ✅ |
| C（queue.ready_queue + RESUME） | ✅ |

**メンション:** `html_text` + 許可タグのみで `@ichiro` リンク展開を確認。**通知:** PAT ユーザー = 承認者 GID のため Asana 仕様上は自己通知されない（別 GID 設定で回避可）。

## 関連

- カーネル delivery: [`org-os-kernelize-delivery.md`](org-os-kernelize-delivery.md)
- 旧 A+B+C E2E: [`approval-flow-e2e-dryrun.md`](approval-flow-e2e-dryrun.md)
- SSOT v2.0: [`../design/org-os-product-io.md`](../design/org-os-product-io.md)
