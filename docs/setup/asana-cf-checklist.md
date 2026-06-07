# Asana カスタムフィールド作成チェックリスト

org-os / org-ops が動作するために、**Asana UI で手動作成**する CF の SSOT 一覧。  
API からフィールド新規作成は行わない前提（GID は sync CLI で `.env` に反映）。

参照: [`docs/design/org-os-product-io.md`](../design/org-os-product-io.md) §5

## 作成手順（プロジェクト単位）

1. Asana プロジェクト → **カスタムフィールド** → 下表どおりに enum フィールドを追加
2. リポジトリルートで GID 同期:

```powershell
python tools/sync_all_cf_env.py --project <PROJECT_GID> --write -y
python tools/org_os.py doctor --online
```

## 必須フィールド

### OS State

| 項目 | SSOT 値 |
|------|---------|
| フィールド名 | `OS State` |
| 型 | enum |
| 選択肢 | `Ready` · `Running` · `Waiting` · `Done` |

用途: epic 状態機械（org-os syscall / queue）

### Approval Required

| 項目 | SSOT 値 |
|------|---------|
| フィールド名 | `Approval Required` |
| 型 | enum |
| 選択肢 | `Yes` · `No` |

### Agent Type

| 項目 | SSOT 値 |
|------|---------|
| フィールド名 | `Agent Type`（旧称 `担当種別` 可） |
| 型 | enum |
| 選択肢 | `AI` · `human` |

用途: org-os `watch` / queue フィルタ（AI + Epic）

### Task Type

| 項目 | SSOT 値 |
|------|---------|
| フィールド名 | `Task Type` |
| 型 | enum |
| 選択肢 | `Intake` · `Epic` |

用途: Intake=依頼入口 · Epic=org-ops エピック

## 推奨（org-os v2）

### OS Suspend Reason

| 項目 | SSOT 値 |
|------|---------|
| フィールド名 | `OS Suspend Reason` |
| 型 | enum |
| 選択肢 | `Approval` · `Human Review` · `External Block` |

**snake_case 禁止** — 表示名は上記と完全一致。

### Approval Result（任意）

| 項目 | SSOT 値 |
|------|---------|
| フィールド名 | `Approval Result` |
| 型 | enum |
| 選択肢 | `OK` · `NG` |

## 作成後の検証

```powershell
python tools/org_os.py doctor --online
python tools/backfill_epic_os_state.py --project <PROJECT_GID> --dry-run
```

- `doctor --online` — CF 名・enum GID が SSOT と一致
- `backfill --dry-run` — OS State 未設定の legacy Epic を列挙

## よくあるミス

| ミス | 症状 |
|------|------|
| enum 名の typo（`ready` 等） | `doctor --online` ERROR |
| OS State 未設定の旧 Epic | queue に出ない → `backfill_epic_os_state.py` |
| 手編集した GID | env と Asana 不一致 → `sync_all_cf_env.py --write -y` |
