# output — 実行時ワークスペース（git 管理外）

各チーム PM / ワーカーの**成果物**を実行時に書き出すローカル領域。本リポジトリは **汎用組織テンプレート** のため、中身は原則 **コミットしない**（`.gitignore`）。

**プロダクト固有の成果物**（アプリ実装・ドメイン用データ・案件別 Handoff 等）はここにのみ置く。汎用テンプレ（`docs/` · `skills/*/examples/`）へは反映しない。

| フォルダ | 用途 |
|----------|------|
| [`planning/`](planning/) | Handoff（`handoff/`）、PlanReviewResult（`plan-review/`） |
| [`development/`](development/) | 要件・設計・仕様・アプリ・レビュー JSON |
| [`analysis/`](analysis/) | データ・モデル・カタログ・レビュー |
| [`ux/`](ux/) | UX 仕様・Design System・レビュー |
| [`platform/`](platform/) | 統括グループの Handoff / plan-review |
| [`dryrun/`](dryrun/) | dryrun 用スタブ（`run_all_teams_dryrun.py` 等） |

**パス convention** は [`workflows/organizations.yaml`](../workflows/organizations.yaml) の `output_root` と各 `*-delivery-io.md` を参照。

**git 管理する fixture:** [`docs/verification/fixtures/`](../docs/verification/fixtures/)（dryrun 用 Handoff JSON）

**PM assign plan:** [`work/assign-plans/`](../work/assign-plans/)（フォルダのみテンプレ）

参照: [`docs/design/artifact-policy.md`](../docs/design/artifact-policy.md)
