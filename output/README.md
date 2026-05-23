# output — 組織別成果物

エージェントの**出力**（Handoff、plan-review、要件書、レビュー JSON 等）を組織ごとに置く。スキル定義は [`skills/`](../skills/)、設計契約は [`docs/design/`](../docs/design/) に残す。

| フォルダ | 用途 |
|----------|------|
| [`planning/`](planning/) | L1 Handoff（`handoff/`）、PlanReviewResult（`plan-review/`） |
| [`development/`](development/) | 要件（`requirements/`）、仕様（`specs/`）、課内レビュー（`reviews/`） |
| [`analysis/`](analysis/) | 分析要件・データモデル・カタログ・インサイト・モデル・リリース・レビュー |
| [`platform/`](platform/) | 横断エピック（基盤整備など）の Handoff / plan-review |

## パス例（スキルから参照）

| 組織 | 例 |
|------|-----|
| 開発課 | `output/development/requirements/<task_gid>.md` |
| 分析課 | `output/analysis/data-model/<task_gid>.md` |
| 企画 | `output/planning/handoff.<theme>.json` |

旧 `work/` は本レイアウトに統合した。セッション用の glob は各組織の `handoff/` / `plan-review/` を指す。
