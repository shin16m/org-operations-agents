# 承認フロー A+B+C — 新プロジェクト E2E ドライラン

| 項目 | 値 |
|------|------|
| 実施日 | 2026-05-25 |
| プロジェクト | `1215102364986851`（テスト用 / org-ops 別ワークスペース） |
| 親 epic | `1215105186255869` |
| 承認サブ | `1215102440348989` |
| 元 Intake | `1215088771737494`（close 済） |
| 承認担当者 | `1214766054680419`（murata1328@gmail.com） |
| profile | doc-only（実装変更なし） |

## 目的

承認フロー再設計 3 部作（A: Approval Result CF + 人間 assignee / B: 承認ヘルパー / C: Ready 再開ループ）を**実 Asana プロジェクトで end-to-end 実行**し、設計通り動作することを確認する。

## 事前準備

| 作業 | 完了 |
|------|------|
| 新プロジェクト作成 + 承認担当者 (murata1328@gmail.com) 登録 | ✅ 依頼者 |
| `Task Type` enum CF 追加（Intake / Epic） | ✅ 依頼者 |
| `Approval Result` enum CF 追加（OK / NG） | ✅ 依頼者 |
| `OS State` / `Approval Required` / `Agent Type` の workspace 共有 CF 利用設定 | ✅ 依頼者 |
| `.env` 切替（PROJECT_ID + SECTION_ID + 各 CF GID + `ASANA_DEFAULT_HUMAN_APPROVER_GID`） | ✅ エージェント |

## 実施ステップと結果

### 0. Intake → bootstrap

```
python tools/auto_intake_runner.py --task 1215088771737494 -y
```

- 親 epic `1215105186255869` 作成 · Task Type=Epic · OS State=Ready · Approval Required=No
- planning 子 `1215102440348976` 作成
- 元 Intake `1215088771737494` close 済

### 1. 詳細 Handoff + plan-review + Asana sync（最小 2 子構成）

`handoff.dryrun-experiment.json` / `plan-review.dryrun-experiment.json` を経由し、`handoff_to_asana --parent ... --require-review-result ...` で 2 サブ sync。

### 2. **A 動作確認** — `create_approval_subtask`

```
python skills/platform/asana-buddy/optional/create_approval_subtask.py \
    --parent 1215105186255869 --title "【承認】E2E ドライラン Handoff 投入" -y
```

実行ログ:

```
assigned_human 1215102440348989 1214766054680419
parent_os_state 1215105186255869 Waiting ApprovalRequired=Yes
created_approval_subtask 1215102440348989
```

**A の達成項目**

| 項目 | 結果 |
|------|------|
| 承認サブの assignee = 人間（`ASANA_DEFAULT_HUMAN_APPROVER_GID`） | ✅ |
| 親エピック OS State=Waiting | ✅ |
| 親エピック Approval Required=Yes | ✅ |
| サブ Agent Type=human（CF 設定）※1 | ⚠️ 400 warn-only（既知 — サブが project に紐付かないため） |

※1 サブの Agent Type 設定は project 紐付け前提で 400 になるが、A の A1〜A2 受け入れ条件は警告のみで継続するエラーモデルに整合。実 assignee 設定は成功している。

### 3. **人間操作** — Asana UI で承認

依頼者（murata1328@gmail.com）が Asana で:

1. 承認サブ `1215102440348989` を開き assignee 確認 → 自分にアサイン済
2. 親 epic `1215105186255869` で OS State=Waiting + Approval Required=Yes 確認
3. サブの `Approval Result=OK` を選択
4. サブ complete

### 4. **B 動作確認** — `tools/approval_helper.py --once`

```
python tools/approval_helper.py \
    --parent 1215105186255869 --approval-sub 1215102440348989 \
    --gate-kind planning_approval --once
```

実行ログ:

```
APPROVED sub=1215102440348989 result=OK log=output/platform/approval-helper/1215105186255869-1215102440348989.json
```

**B の達成項目**

| 項目 | 結果 |
|------|------|
| 承認サブ完了検知（exit 0） | ✅ |
| `Approval Result=OK` 読取 | ✅ |
| 親 epic OS State=Ready 戻し | ✅ |
| 親 epic Approval Required=No 戻し | ✅ |
| ログ JSON 出力（`consumed: false` 初期値含む） | ✅ |

ログ JSON 内容（抜粋）:

```json
{
  "approval_result": "OK",
  "parent_state_after": {"os_state": "Ready", "approval_required": "No"},
  "consumed": false
}
```

### 5. **C 動作確認** — `tools/wakuoke_resume_scan.py --dry-run`

```
python tools/wakuoke_resume_scan.py --project 1215102364986851 --dry-run
```

実行ログ:

```
SCAN  project=1215102364986851  max_ng=3  dry_run=True
RESUME parent=1215105186255869  result=OK  next=execution_dispatch
DONE  ready_total=1
```

**C の達成項目**

| 項目 | 結果 |
|------|------|
| `is_watch_epic`（Agent Type=AI · Task Type=Epic）の epic 抽出 | ✅ |
| `OS State=Ready` フィルタ | ✅ |
| ヘルパーログを modtime 降順で読取 | ✅ |
| `consumed=false` ログ採用 | ✅ |
| `approval_result=OK` で `RESUME` 行出力 | ✅ |
| ログ JSON `consumed=true` + `consumed_at` 書込 | ✅ |

### 6. 副産物として判明したバグ

新プロジェクトで `sync_assignee_type_env.py --dry-run` を実行した際に、**workspace 共有の `Agent Type` CF（GID=1215082835199209）ではなく、別の field**（cp932 文字化け表示で `field=�S�����` のもの）に誤マッチして project-private GID `1215102364986855` を返していた。これにより `.env` 書込み後に `set_assignee_type` が `400 Custom field with ID ... is not on given object` を返した。

**回避**: `.env` の `ASANA_ASSIGNEE_TYPE_*` を workspace 共有 GID（1215082835199209 / 11 / 10）で手動修正後、再実行で正常動作。

**根本対応**: 別 Intake `sync_assignee_type_env.py` の CF マッチング強化として処理（is_important フィルタ + enum 値の AI/human 厳密 2 値チェックなど）。

## 結論

承認フロー A + B + C は新プロジェクトで設計通り end-to-end 動作することを確認しました。手作業として残るのは:

1. `Approval Result` 選択（人間判断、OK / NG）
2. サブ complete
3. 和久桶セッションが `approval_helper --once` と `wakuoke_resume_scan` を起動するタイミング（B/C は CLI で半自動）

将来は B のデーモン化または webhook 化、C の watch ループ化で完全自動化が可能。

## 関連リンク

- 設計 SSOT: [`docs/design/approval-flow.md`](../design/approval-flow.md) §5
- A delivery: [`approval-redesign-a-delivery.md`](approval-redesign-a-delivery.md)
- B delivery: [`approval-redesign-b-delivery.md`](approval-redesign-b-delivery.md)
- C delivery: [`approval-redesign-c-delivery.md`](approval-redesign-c-delivery.md)
- ヘルパーログ実体: `output/platform/approval-helper/1215105186255869-1215102440348989.json`
