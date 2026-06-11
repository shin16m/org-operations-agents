# 初回 qa pass 率 85% — 検証記録

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-11 |
| 子 GID | `1215475359795553` |
| 目標 | ≥ 85% |

## aggregate_delivery_kpi

```powershell
python tools/aggregate_delivery_kpi.py --json
```

| 指標 | M6 目標 | M9 目標 | 実測（2026-06-11） |
|------|---------|---------|-------------------|
| 初回 qa pass 率 | 70% | **85%** | ロードマップ Epic フィルタで **100%**（1 件） |

## 所見

M6 代表 E2E 1 件は初回 pass。組織全体 85% は **今後の execution Epic 蓄積**で再計測。未達時 retro 候補: completion_score 記録徹底 · full-ui 初回 qa 強化 · dev-reviewer EC 事前チェック。
