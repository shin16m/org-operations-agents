# M6 — 直近3エピック品質監査（verification 写し）

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-11 |
| 監査子 GID | `1215475359998592` |
| ロードマップ Epic | `1215475353160824` |
| SSOT 監査記録 | [`output/governance/records/1215475359998592-quality-gap-audit.md`](../../output/governance/records/1215475359998592-quality-gap-audit.md) |

## 監査対象

| Epic GID | タイトル |
|----------|----------|
| `1215474826616152` | 納品完成度 50%→80% |
| `1215475080199865` | 納品品質 follow-up（M4） |
| `1215475084856660` | レトロ/intake Phase 2（M5） |

## 検証コマンド

```powershell
cd E:\data\document\sourse\org-operations-agents
$env:PYTHONIOENCODING='utf-8'
python tools/aggregate_epic_retrospective.py --parent 1215474826616152
python tools/aggregate_epic_retrospective.py --parent 1215475080199865
python tools/aggregate_epic_retrospective.py --parent 1215475084856660
python tools/validate_org_registry.py
python tools/validate_fixture_schemas.py
python tools/validate_ssot_contract.py
```

| コマンド | 期待 |
|----------|------|
| aggregate × 3 | epic-retro.json 生成 · tasks=0（ギャップとして記録） |
| validate 3 本 | exit 0 |

## 完了条件（done_when）

- [x] 監査記録 md 保存（records + 本 verification md）
- [x] M6 KPI 目標値との差分表あり
- [x] governance review passed（`output/governance/reviews/1215612214919955-governance.review.json`）

## M6 ブロック次手

Execution Order 4 以降: full-ui E2E → completion_score enforcement → 依頼者サマリ → KPI CLI → M6 トラッカー。
