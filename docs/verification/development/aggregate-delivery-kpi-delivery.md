# KPI ダッシュボード CLI — delivery 記録

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-11 |
| 親子 GID | `1215475465759613` |
| ロードマップ Epic | `1215475353160824` |

## 実装

| パス | 内容 |
|------|------|
| `tools/aggregate_delivery_kpi.py` | 初回 qa pass 率 · fix 平均ラウンド · completion_score 平均 |
| `tools/test_aggregate_delivery_kpi.py` | unittest 1 件 |

## 検証

```powershell
cd E:\data\document\sourse\org-operations-agents
python tools/aggregate_delivery_kpi.py --help
python -m unittest tools.test_aggregate_delivery_kpi -v
python tools/aggregate_delivery_kpi.py --parent 1215475353160824 --json
```

## KPI 算出（SSOT 一致）

| KPI | 算出 |
|-----|------|
| 初回 qa pass 率 | 各 development 子の**初回** verification `passed*` / 子数 |
| fix 平均ラウンド | `[fix]` 相当（同一 task の 2 件目以降 verification）/ 子数 |
| completion_score 平均 | worker レトロ JSON の `completion_score` 平均 |

## 現状スナップショット（2026-06-11）

ロードマップ Epic `--parent 1215475353160824` 実行時、verification / retro 実データ不足のため各 KPI は `null` または 0 件 — M6 子 4（full-ui E2E）完了後に再計測。
