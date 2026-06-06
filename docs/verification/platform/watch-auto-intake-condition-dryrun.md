# watch auto intake 条件変更 — dryrun

| エピック | `1215466151241228` |
| development 子 | `1215466151566927` |

## 変更

- `is_candidate` からタスク名 `【org-ops】` プレフィックス判定を削除
- Task Type=Intake + Agent Type=AI のみで intake 候補を判定

## 検証

```powershell
python tools/asana_ops_poller.py --once --dry-run
```

- exit 0（Windows cp932 環境で UnicodeEncodeError なし）
- Intake CF 付き・プレフィックスなしタスクが CANDIDATE として列挙可能
