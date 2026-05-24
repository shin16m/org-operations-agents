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
.\.venv\Scripts\python.exe -c @"
import sys
sys.path.insert(0, 'skills/platform/asana-buddy/optional')
from agent_handler_asana import get_token, load_env_from_dotfile
from asana_program_common import remove_task_from_project, resolve_project_with_fallback
load_env_from_dotfile()
token = get_token()
project = resolve_project_with_fallback(None)
for gid in ['1215085933918188']:  # 対象サブタスク GID を列挙
    remove_task_from_project(gid, project, token)
    print('removed', gid)
"@
```

Asana UI で親エピック配下のみ表示されることを確認。

## 参照

- commit 修正: `create_subtask` から `ensure_subtask_project_membership` 撤回
