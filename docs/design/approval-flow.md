# 人間承認フロー — SSOT

承認サブタスク（【承認】/【レビュー】）と OS State 機械・Approval Required・Approval Result CF の関係を定義する。

関連:
- [`org-os-product-io.md`](org-os-product-io.md) §4 Asana CF · §5 状態遷移
- [`planning-gate-vs-pm-review-gate.md`](planning-gate-vs-pm-review-gate.md) gate 種類
- [`pm-assign-review-gate.md`](pm-assign-review-gate.md) PM レビュー gate
- 実装: [`skills/platform/asana-buddy/optional/create_approval_subtask.py`](../../skills/platform/asana-buddy/optional/create_approval_subtask.py)

## 1. CF 構成

| CF | 値域 | 起票時 | 完了時（人間が設定） | 備考 |
|----|------|--------|----------------------|------|
| **OS State** | Ready / Running / Waiting / Done | `Waiting` を親に設定 | `Ready` に遷移（B 承認ヘルパー / 後続 epic） | 承認サブ自体ではなく**親エピック**の状態 |
| **Approval Required** | Yes / No | `Yes` を親に設定 | `No`（B 承認ヘルパー / 後続 epic） | 親エピックの flag |
| **Approval Result** | OK / NG / **未設定 (=pending)** | **未設定**（=pending） | 人間が承認サブ完了時に **OK** または **NG** を選択 | 承認サブ自体に設定 · pending は明示的に書かない |

CF 追加と env 同期は [`tools/sync_org_os_cf_env.py`](../../tools/sync_org_os_cf_env.py)（`Approval Result` は **optional** — 未追加でも他 CF の同期は継続）。

## 2. 承認サブ起票時の動作（A — 本ドキュメント策定時点）

`create_approval_subtask.py` 実行時:

1. 承認サブ作成（Asana subtask）
2. サブの `Agent Type=human` 設定
3. サブの `assignee` を **`ASANA_DEFAULT_HUMAN_APPROVER_GID`** の人間ユーザーに設定
   - env 未設定なら警告のみ。CI 環境などで人間 assignee が無いケースを想定
   - 将来 `gate_kind`（planning_approval / pm_review_gate）別の上書きを可能にする拡張枠あり
4. **親エピック**の `OS State=Waiting`
5. **親エピック**の `Approval Required=Yes`

すべて警告のみで処理継続（CF / env 未整備でも作成自体は失敗させない）。`Approval Result` は触らない（pending を維持）。

## 3. 人間の承認動作

承認担当者は Asana UI で以下を行う:

| 結果 | 操作 | 後続 |
|------|------|------|
| OK | 承認サブの `Approval Result=OK` を選択 → 完了 | B（承認ヘルパー）が検知 → 親 `Approval Required=No` · `OS State=Ready` → 和久桶が再開 |
| NG | 承認サブにコメント追記 → `Approval Result=NG` を選択 → 完了 | B が検知 → 親 `Approval Required=No` · `OS State=Ready` → 和久桶が再開 → C（NG 差し戻しループ）でコメント反映 |
| 差し戻し（旧運用） | 承認サブを未完了のまま親へコメント | 互換のため B では「Result 未設定で完了」を **NG** と同等に扱う方針（C で実装） |

## 4. 状態遷移（親エピック）

```
[Running]
   │ create_approval_subtask
   ▼
[Waiting] + ApprovalRequired=Yes
   │ 承認サブ完了 (B 承認ヘルパー)
   ▼
[Ready] + ApprovalRequired=No
   │ ApprovalResult=OK → 和久桶 dispatch
   │ ApprovalResult=NG → 和久桶 NG 差し戻し (C)
```

`state_machine.py` API は `need_approval` / `approval_done` / `complete` を提供。本ドキュメントは Asana CF 側の写像を SSOT 化したもの。

## 5. 段階的実装スコープ

| Epic | 範囲 | ステータス |
|------|------|------------|
| **A** Approval Result CF + 人間 assignee 連携 | 起票時の **書込み** すべて（OS State/ApprovalRequired/assignee）· Approval Result CF env 同期 | 実装済 |
| **B** 承認ヘルパー | 完了検知 + 親 CF 戻し（OS State→Ready, ApprovalRequired→No）· `tools/approval_helper.py` + `read_approval_result` | 実装済 |
| **C** Ready 再開ループ | OS State=Ready epic の resume scanner · NG コメント反映 · NG ループ上限 + escalation · `tools/wakuoke_resume_scan.py` | 実装済 |

### 5.1 B 承認ヘルパー CLI 仕様

実装: [`tools/approval_helper.py`](../../tools/approval_helper.py)

```
python tools/approval_helper.py \
    --parent <EPIC_GID> --approval-sub <SUB_GID> \
    --gate-kind <planning_approval|pm_review_gate> \
    [--interval 30] [--timeout 604800] [--once] \
    [--log-dir output/platform/approval-helper]
```

| exit | 意味 |
|------|------|
| 0 | 承認検知 → 親 CF を Ready/No に戻し → ログ JSON 出力 |
| 1 | `--once` で承認サブが pending（ログ未出力） |
| 2 | 承認サブが見つからない |
| 124 | `--timeout` 超過 |

ログ JSON スキーマ:

```json
{
  "helper_version": "1.0",
  "parent_gid": "...",
  "approval_sub_gid": "...",
  "gate_kind": "planning_approval",
  "started_at": "ISO8601",
  "completed_at": "ISO8601",
  "approval_result": "OK | NG | null",
  "approval_comments_excerpt": "<= 200 chars",
  "parent_state_after": {"os_state": "Ready", "approval_required": "No"}
}
```

CF / env 未設定の場合は `parent_state_after` が `unchanged` となり、`approval_result` が `null` になる（A の警告のみで継続するエラーモデル踏襲）。

**`--parent` の意味:** 承認サブがぶら下がる **wait_target**（planning gate では親 epic GID · PM review gate では **PM 子 GID**）。`approval_helper` は内部で `resolve_epic_gid` により epic に `syscall.resume` する。

### 5.2 runner サイクル内の B→C 順序（`asana_ops_runner`）

watch-auto / [`tools/asana_ops_runner.py`](../../tools/asana_ops_runner.py) は **1 サイクル**で次の順序を守る（delivery: [`runner-resume-approval-helper-delivery.md`](../verification/platform/runner-resume-approval-helper-delivery.md)）:

```
run_approval_helper_pass   # suspended · approval_sub_gid complete → helper (--parent=wait_target)
scan_projects              # RESUME approved → run_session_approval_helper（kick しない）
scan_resume_and_dispatch   # Ready queue → org_os START → DISPATCH / kick
scan_execution_and_kick    # Running epic L3b bridge
archive_resumable_sessions
```

| ルール | 内容 |
|--------|------|
| resumable 判定 | `session.approval_sub_gid` の `completed` を正とする（marker 曖昧一致禁止） |
| 二重 kick 禁止 | `scan_projects` から `_session_auto_kick` を呼ばない（後段 resume scan に委譲） |
| 期待ログ | `HELPER`/`APPROVED` → `RESUME` → `START` → `DISPATCH` |

### 5.3 関連実装関数（B 追加分）

| 関数 | 用途 |
|------|------|
| `get_task_custom_fields(task_gid, token)` | 単発タスクの custom_fields を `{field_gid: {name, enum_value}}` で取得 |
| `read_approval_result(task_gid, token)` | Approval Result enum option 名（OK / NG / None）を返す |

### 5.4 C resume scanner CLI 仕様

実装: [`tools/wakuoke_resume_scan.py`](../../tools/wakuoke_resume_scan.py)

```
python tools/wakuoke_resume_scan.py \
    [--project <PROJECT_GID>] [--max-ng 3] [--dry-run] \
    [--escalation-user <USER_GID>]
```

**出力語彙**

| 行頭 | 意味 |
|------|------|
| `SCAN` | スキャン開始（project / max_ng / dry_run を表示） |
| `READY` | Ready epic でヘルパーログ無し（fresh dispatch lane） |
| `RESUME` | Ready epic で `consumed=false` ヘルパーログあり、再開可能（OK / NG 双方） |
| `ESCALATE` | NG ループが `--max-ng` に到達。親 epic に escalation コメント投稿（dry-run 時は出力のみ） |
| `DONE` | スキャン完了サマリ |

**処理フロー**

1. `is_watch_epic` で Agent Type=AI · Task Type=Epic を抽出
2. `read_os_state` が Ready かつ `read_approval_required` が Yes でないものに絞る
3. `output/platform/approval-helper/<parent>-*.json` を modtime 降順、最初に見つかった `consumed=false` ログを採用
4. `approval_result` で分岐:
   - `OK`: `RESUME ... result=OK` 出力 + ログを `consumed=true` 更新
   - `NG` / `null`: NG counter `output/platform/approval-helper/ng-counters/<parent>.json` を increment し、`history` に最大 10 件保持
     - `ng_count < max_ng`: `RESUME ... result=NG count=<n>/<max>` 出力
     - `ng_count >= max_ng`: `ESCALATE ... count=<n>/<max>` 出力 + `_post_escalation_comment`
5. 全件処理後 `DONE  ready_total=<n>` 出力

**NG counter ファイル**

```json
{
  "parent_gid": "...",
  "ng_count": 2,
  "max_ng": 3,
  "updated_at": "ISO8601",
  "history": [
    {"sub_gid": "...", "completed_at": "...", "result": "NG", "excerpt": "<= 200 chars"}
  ]
}
```

**ヘルパーログの consumed フラグ**

`approval_helper.py` は書出し時に `consumed: false` を初期値で含める。resume scanner が処理したログは `consumed: true` + `consumed_at` を書き戻して二重カウントを防止する。

**スコープ外（C ではやらない）**

- 自動 execution dispatch（resume 後の dispatch は和久桶セッションが Asana コメントを読んで人間判断）
- planner / PM 自動再起動
- Webhook（既存 polling MVP 路線維持）

## 6. env キー

| env キー | 用途 |
|---------|------|
| `ASANA_APPROVAL_RESULT_FIELD_GID` | Approval Result CF GID（optional） |
| `ASANA_APPROVAL_RESULT_OK_GID` | OK enum GID |
| `ASANA_APPROVAL_RESULT_NG_GID` | NG enum GID |
| `ASANA_DEFAULT_HUMAN_APPROVER_GID` | 承認サブの assignee に設定する Asana ユーザー GID |

テンプレート: [`skills/platform/asana-buddy/optional/.env.example`](../../skills/platform/asana-buddy/optional/.env.example)

## 7. 関連実装（org-os syscall / asana_program_common）

| コンポーネント | 用途 |
|----------------|------|
| `org_os.syscall.suspend(parent, "Approval", ref=sub_gid)` | 親 epic → Waiting + OS Suspend Reason=**Approval**（Asana 表示名） + Approval Required=Yes |
| `org_os.syscall.resume(parent, ref=sub_gid)` | 承認完了後 Waiting → Ready（`approval_helper`） |
| `create_approval_subtask` | サブ作成 · human assignee · suspend · subtask へ **html_text** `@`-mention（`data-asana-type="user"` · **`br`/`p` 等は不可**） |

**@-mention 注意（2026-05-26 検証）:**

1. **plain `text` の `<@gid>` は無効** — `html_text` + `<a data-asana-type="user" data-asana-gid="..."></a>` が必須
2. **Stories の許可タグのみ** — `body`, `strong`, `em`, `a`, `ul`, `li` 等。**`<br/>` を入れると HTML 全体がエスケープされメンションが壊れる**
3. **通知** — assignee / follower 設定後に mention。さらに **PAT ユーザーと承認者が同一 GID の場合、自分自身への通知は Asana 側で飛ばない**（別ユーザー GID を `ASANA_DEFAULT_HUMAN_APPROVER_GID` に設定すること）
| `approval_result_config()` | Approval Result CF GID 取得（未設定時 None） |
| `human_approver_gid()` | 人間 assignee GID 取得（未設定時 None） |
| `assign_user(task_gid, user_gid, token)` | Asana 標準 assignee 設定 |
| `set_assignee_type_human(sub_gid, token)` | 承認サブの Agent Type=human |

**禁止:** org-ops から `set_org_os_custom_fields(..., os_state="waiting")` で親 epic を直接 Waiting にしない（syscall 経由のみ）。
