# completion_score worker レトロ必須 — delivery 記録

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-11 |
| 親子 GID | `1215475353211405` |
| ロードマップ Epic | `1215475353160824` |

## 実装

| パス | 内容 |
|------|------|
| `tools/record_task_retrospective.py` | `--completion-score` 必須（0–100） |
| `tools/check_task_retrospective.py` | 欠落 · 範囲外で exit 1（`--no-require-completion-score` で legacy） |
| `tools/test_check_task_retrospective.py` | unittest 5 件 |
| `docs/design/task-retrospective-ssot.md` | completion_score 必須節追記 |

## 検証

```powershell
cd E:\data\document\sourse\org-operations-agents
python -m unittest tools.test_check_task_retrospective -v
python tools/record_task_retrospective.py --task 999 --agent developer --completion-score 80 --went-well x
python tools/check_task_retrospective.py --task 999
python tools/check_task_retrospective.py --task 999 --no-require-completion-score
```

| コマンド | 結果 |
|----------|------|
| unittest | exit 0 |
| record + check | exit 0 |

## SSOT 整合

`delivery-completion-standard.md` § KPI の completion_score と算出式一致。
