# Asana 担当種別 CF — dryrun 記録

| エピック | `1215101173313877` |
| development 子 | `1215085934023360` |
| ソース | `1215082835252581` |

## 検証

```powershell
# CF 一覧（プロジェクト）
# GET custom_field_settings → 担当種別 1215082835199209 · AI 1215082835199211 · human 1215082835199210

# create_subtask 経由で AI が付く（pm_assign_subtasks / handoff_to_asana）
python -c "
from pathlib import Path
import sys
sys.path.insert(0, 'skills/platform/asana-buddy/optional')
from agent_handler_asana import get_token, load_env_from_dotfile
from asana_program_common import create_subtask, fetch_task, ASANA_BASE
import requests
load_env_from_dotfile()
token = get_token()
# 既存親の下にテストサブは作らず、set_assignee_type の API 200 を企画子で確認済
"
```

## 実装

- `set_assignee_type` / `set_assignee_type_org_ops` in `asana_program_common.py`
- `create_subtask` 作成直後に `AI`
- `handoff_to_asana.py` 親 create 直後に `AI`
- `.env.example` + `docs/design/asana-assignee-type-field.md`

## 参照

- SSOT: [`docs/design/asana-assignee-type-field.md`](../design/asana-assignee-type-field.md)
