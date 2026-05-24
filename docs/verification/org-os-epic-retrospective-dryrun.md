# org-os + triage エピック — レトロスペクティブ dryrun

| 項目 | 内容 |
|------|------|
| エピック | `1215088809649925`（complete 済み · レトロは事後実施） |
| 承認サブ | `1215088874066920` 【承認】レトロ改善候補 → intake 起票 |
| 日付 | 2026-05-24 |

## 実施

### タスク単位 retro（5 件）

| task_gid | agent |
|----------|-------|
| `1215102426500444` | developer（【2/5】） |
| `1215102425601682` | developer（【3/5】） |
| `1215088968942698` | qa-verifier |
| `1215089090005287` | ssot-implementer |
| `1215089026749599` | consistency-auditor |

### エピック集約

- `output/platform/retrospectives/1215088809649925-epic-retro.json`
- **7 intake 候補**（他 epic 混入を手動除外）

### intake 承認 gate

```powershell
python tools/create_retrospective_intake_gate.py `
  --parent 1215088809649925 `
  --retro output/platform/retrospectives/1215088809649925-epic-retro.json -y
```

## intake 候補（7 件）

1. execution 開発子 PM lite assign 初手必須
2. assign plan [retro] Phase 2 同梱
3. legacy epic OS State バックフィル CLI
4. org-os watch → poller ダッシュボード連携
5. default v4 README/e2e 横展開
6. epic complete 前レトロ gate WARN
7. aggregate_epic_retrospective --parent フィルタ

## 承認後 CLI

```powershell
python tools/check_retrospective_intake_gate.py --parent 1215088809649925
python tools/create_retrospective_intake_tasks.py `
  --parent 1215088809649925 `
  --retro output/platform/retrospectives/1215088809649925-epic-retro.json -y
```

## 所見

- 本エピックは **complete → レトロ** の順序逆転（候補 6 に反映）
- `aggregate_epic_retrospective.py` は全 `*-retro.json` を拾う — 本 epic では手動フィルタ（候補 7）

## 関連

- SSOT: [`task-retrospective-ssot.md`](../design/task-retrospective-ssot.md)
- delivery: [`org-os-governance-audit-delivery.md`](org-os-governance-audit-delivery.md)
