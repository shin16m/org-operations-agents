# UX delivery v2 — dry-run 実行記録

実施: 2026-06-06 00:38 UTC

## 目的

`ux-delivery` v2（profile: flagship）の PM サブタスク分解・**ux-designer / design-system-owner / ux-reviewer（design_quality + ux_spec）** が `comment_task` → `complete_task` まで到達することを Asana 上で確認する。

## 実行

```powershell
$env:PYTHONIOENCODING='utf-8'
tools/run_ux_v2_dryrun.py --ux-child 1215465979480152 --parent 1215465898936132
```

## fixture

| 種別 | パス |
|------|------|
| bootstrap | `docs/verification/fixtures/planning/handoff/bootstrap.ux-v2-dryrun.json` |
| assign plan | `skills/ux/examples/assign-plan.dryrun-v2.json` |

## Asana

| 項目 | 値 |
|------|-----|
| 親エピック GID | `1215465898936132` |
| UX 子 GID | `1215465979480152` |

## 結果

- workers（順）: ux-designer, ux-reviewer, design-system-owner, ux-reviewer
- 期待ロール: ux-designer, ux-reviewer, design-system-owner, ux-reviewer
- サブタスク数: 4
- design-system-owner: 到達確認

## stub 成果物

- `output\dryrun\ux\1215465979480152-ux-spec.md`
- `output\dryrun\ux\1215465979480152-design-system.md`
- `https://www.figma.com/design/dryrun-ux-v2-ui`
- `https://www.figma.com/design/dryrun-ux-v2-ds`

## チェックリスト

- [x] ux-pm が assign-plan.dryrun-v2.json でサブタスク分解
- [x] design-system-owner サブが存在
- [x] 各ワーカーが comment_task → complete
- [x] ux-pm が親を complete
- [x] stub に Figma URL を含む

## 手動実行（参考）

```powershell
$env:PYTHONIOENCODING='utf-8'
python tools/run_ux_v2_dryrun.py
# 既存 Epic 再利用:
python tools/run_ux_v2_dryrun.py --parent <EPIC_GID>
python tools/run_ux_v2_dryrun.py --ux-child <UX_CHILD_GID> --parent <EPIC_GID>
```

一括 dryrun（全チーム）の UX 段階も v2 plan を使用: `python tools/run_all_teams_dryrun.py`

## 関連

- [`ux-delivery-io.md`](../design/ux-delivery-io.md)
- [`ux-pm-assignment.md`](../design/ux-pm-assignment.md)
- [`run_ux_v2_dryrun.py`](../../tools/run_ux_v2_dryrun.py)
- 索引: [`docs/verification/README.md`](README.md)
