# MS3 dryrun — M5 トラッカー再評価デモ

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-09 |
| 対象 | 完成度100%ロードマップ M5 トラッカー `1215475369302645` |
| checklist | `docs/verification/fixtures/milestone-readiness/m5-learning-loop.json` |

## 背景

M5 は 2026-06-08 に complete 済みだが、依頼者振り返りで実運用ギャップ（gate · [retro] 未展開等）が判明。MS3 手順を**過去トラッカーに適用したら何が起きるか**を記録する。

## 実行

```powershell
python tools/check_milestone_readiness.py `
  --checklist docs/verification/fixtures/milestone-readiness/m5-learning-loop.json `
  --tracker-gid 1215475369302645 `
  --out output/governance/milestone-reports/1215475369302645-readiness.json

python tools/epic_milestone_readiness_hook.py --task 1215475369302645 --dry-run
```

## 結果（2026-06-09 時点リポジトリ）

| 項目 | 値 |
|------|-----|
| score | 85.0 |
| status | achieved |
| gaps | 1（例: retro JSON 強制未達の rg 項目） |

## 所見

- **MS2 以前:** 子 Epic complete + 限定的 unittest のみでトラッカーが閉じ得た
- **MS3 以降:** 上記コマンドがトラッカー complete 前の**必須手順**（governance-pm SKILL）。`ORG_OPS_MILESTONE_READINESS_BLOCK=1` で未達時は hook が exit 1
- M5 トラッカーは現 checklist では achieved だが、依頼者振り返りで挙がった P0/P1（M5.1）は **checklist 強化**で今後 fail にできる（MS4）

## 検証

`python -m unittest tools.test_epic_milestone_readiness_hook -v`
