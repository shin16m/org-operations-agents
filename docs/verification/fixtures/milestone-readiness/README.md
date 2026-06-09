# マイルストーン readiness checklist fixtures

SSOT: [`docs/design/milestone-effectiveness-standard.md`](../../../design/milestone-effectiveness-standard.md)

| fixture | マイルストーン |
|---------|----------------|
| `m4-enforcement.json` | M4 80% Enforcement |
| `m5-learning-loop.json` | M5 学習ループ閉鎖 |
| `m6-kpi-measurement.json` | M6 80% 実測（KPI） |
| `m7-ops-hardening.json` | M7 運用インフラ硬化 |
| `m8-quality-ssot.json` | M8 100% 品質 SSOT |
| `m9-completion-100.json` | M9 完成度100% 達成 |

検証:

```powershell
python tools/check_milestone_readiness.py --checklist docs/verification/fixtures/milestone-readiness/m5-learning-loop.json
```
