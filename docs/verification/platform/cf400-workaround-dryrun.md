# CF 400 workaround · sync_assignee_type_env — dryrun

| エピック | `1215087267057946` |
| development 子 | `1215087739926668` |

## CLI

```powershell
python tools/sync_assignee_type_env.py --project 1214771428861230 --dry-run
python tools/sync_assignee_type_env.py --project 1215102364986851 --dry-run
python tools/validate_ssot_contract.py
```

## 結果

| プロジェクト | field | AI | human |
|-------------|-------|-----|-------|
| 1214771428861230 | 1215082835199209 | 1215082835199211 | 1215082835199210 |
| 1215102364986851 | 1215102364986855 | 1215102364986857 | 1215102364986856 |
