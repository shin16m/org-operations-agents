# Asana サブタスク構成修正 — dryrun 記録

| エピック | `1215086038995602` |
| development 子 | `1215101195988417` |
| ソース | `1215082835252584` |

## 症状

`0facbd3` 以降、`create_subtask` が `addProject` したサブタスクが section `1214772665399078` **直下**に表示される（例: `1215085933918188`）。

## 修正

- `create_subtask`: **addProject しない** / サブタスクに担当種別 CF を付けない
- 担当種別 CF は **エピック親のみ**（`handoff_to_asana.py` create/sync）
- SSOT: [`docs/design/asana-assignee-type-field.md`](../design/asana-assignee-type-field.md) v1.1

## 受け入れ基準

1. 新規 `create_subtask` 後、サブタスクがプロジェクト一覧・セクション直下に **出ない**
2. エピック親の担当種別 CF = `AI` は維持
3. 既存誤配置は任意バックフィル（下記）

## 既存サブタスクのバックフィル（任意）

誤って `addProject` されたサブタスクをプロジェクトから外す:

```powershell
$env:PYTHONIOENCODING="utf-8"
# 一覧のみ
.\.venv\Scripts\python.exe .\tools\backfill_subtask_project_membership.py --dry-run
# 実行
.\.venv\Scripts\python.exe .\tools\backfill_subtask_project_membership.py
```

特定 GID のみ:

```powershell
.\.venv\Scripts\python.exe .\tools\backfill_subtask_project_membership.py --gid 1215085933918188
```

Asana UI で親エピック配下のみ表示されることを確認。

## 参照

- commit 修正: `create_subtask` から `ensure_subtask_project_membership` 撤回
