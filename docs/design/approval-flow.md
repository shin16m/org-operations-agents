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
| **A** Approval Result CF + 人間 assignee 連携 | 起票時の **書込み** すべて（OS State/ApprovalRequired/assignee）· Approval Result CF env 同期 | 本ドキュメント策定（実装済 / governance 配賦中） |
| **B** 承認ヘルパー | 完了検知 + 親 CF 戻し（OS State→Ready, ApprovalRequired→No）· session JSON 拡張 | 別 Intake `1215089409856284` |
| **C** Ready 再開ループ | OS State=Ready epic の自動 resume · NG コメント反映 · NG ループ上限 | 別 Intake `1215102436390998` |

## 6. env キー

| env キー | 用途 |
|---------|------|
| `ASANA_APPROVAL_RESULT_FIELD_GID` | Approval Result CF GID（optional） |
| `ASANA_APPROVAL_RESULT_OK_GID` | OK enum GID |
| `ASANA_APPROVAL_RESULT_NG_GID` | NG enum GID |
| `ASANA_DEFAULT_HUMAN_APPROVER_GID` | 承認サブの assignee に設定する Asana ユーザー GID |

テンプレート: [`skills/platform/asana-buddy/optional/.env.example`](../../skills/platform/asana-buddy/optional/.env.example)

## 7. 関連実装関数（asana_program_common）

| 関数 | 用途 |
|------|------|
| `approval_result_config()` | Approval Result CF GID 取得（未設定時 None） |
| `human_approver_gid()` | 人間 assignee GID 取得（未設定時 None） |
| `assign_user(task_gid, user_gid, token)` | Asana 標準 assignee 設定 |
| `set_org_os_custom_fields(parent, ..., os_state="waiting", approval_required="yes")` | 親 epic の OS State + Approval Required を一括設定 |
| `set_assignee_type_human(sub_gid, token)` | 承認サブの Agent Type=human |
