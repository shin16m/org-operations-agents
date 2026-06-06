# UX → development full-ui — 継ぎ目 dryrun

実施: 2026-06-06 01:19 UTC

## 目的

UX 子単体ではなく、**UX 完了 → product-manager が `## 依存` 転記 → full-ui 着手**までのチーム間継ぎ目を Asana 上で確認する。

## 実行

```powershell
$env:PYTHONIOENCODING='utf-8'
.\tools\run_ux_to_dev_full_ui_dryrun.py
```

## fixture

| 種別 | パス |
|------|------|
| bootstrap | `docs/verification/fixtures/planning/handoff/bootstrap.ux-to-dev-full-ui-dryrun.json` |
| UX assign plan | `skills/ux/examples/assign-plan.dryrun-v2.json` |
| dev assign plan | `skills/development/examples/assign-plan.full-ui-v1.json` |

## Asana

| 項目 | GID |
|------|-----|
| 親エピック | `1215466257349499` |
| UX 子 | `1215479468177507` |
| 開発子（full-ui） | `1215465981793109` |

## 継ぎ目チェック

- [x] UX 子: ux-pm が v2 全ワーカー完了 · Figma stub を artifacts に含む
- [x] 開発子: `## 依存（読み取り専用）` に UX 仕様パス + Figma URL が転記されている
- [x] 開発子: `profile: full-ui` ヘッダのあとに依存表
- [x] Figma UI stub: `https://www.figma.com/design/dryrun-ux-to-dev-ui`（実在ファイルではない）
- [x] product-manager が pm_assign 後、full-ui ワーカーが comment → complete

## 結果

- UX workers: ux-designer, ux-reviewer, design-system-owner, ux-reviewer
- dev workers: requirements-writer, dev-reviewer, tech-designer, dev-reviewer, developer, dev-reviewer, ux-reviewer, qa-verifier, requirements-writer, dev-reviewer

## 関連

- [`cross-team-artifact-bridge.md`](../design/cross-team-artifact-bridge.md)
- [`ux-delivery-v2-dryrun.md`](ux-delivery-v2-dryrun.md)
- [`run_ux_to_dev_full_ui_dryrun.py`](../../tools/run_ux_to_dev_full_ui_dryrun.py)
