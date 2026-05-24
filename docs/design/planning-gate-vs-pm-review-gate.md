# planning gate と PM review gate — 整理 SSOT

| 版 | 1.0 |
| 日付 | 2026-05-24 |
| エピック | `1215086341081688` · F4 |

## 2 種類の人間ゲート

| ゲート | 段階 | 担当 PM | 承認対象 | トリガー CLI | チェック CLI |
|--------|------|---------|----------|--------------|--------------|
| **planning gate** (`handoff_approved`) | L3 企画 | planning-pm | Handoff 要約 · execution 系子の Asana 投入 | `handoff_to_asana.py --require-review-result` | （チャット明示承認 + PlanReviewResult） |
| **PM review gate** (`pm_review_gate`) | L3 execution 各 PM | product-manager / ux-pm / analytics-pm / governance-pm / audit-pm | **作成済み worker サブ**の構成・担当 slug | `create_pm_review_gate.py` | `check_pm_review_gate.py` exit 0 |

## 混同しやすい点

- **planning gate の「承認」** = execution 系子タスクを Asana に**作ってよい**（実装開始の合図**ではない**）。
- **PM review gate の「完了」** = 当該 PM 子の **L3b worker dispatch 可**（`pm_emit_worker_prompt` 前）。
- チャットの「すすめて」「承認」は **planning gate のみ**有効。PM review gate は **Asana UI で【レビュー】サブを complete** する。

## F1: Asana dependencies

`create_pm_review_gate.py` 実行後、各 worker サブは【レビュー】サブに **Asana dependency** を付与する（`addDependencies`）。  
人間が review サブを complete するまで worker サブは Asana 上もブロックされる。

## 参照

- [`workflow-io-contract.md`](workflow-io-contract.md) — パイプライン全体
- [`pm-assign-review-gate.md`](pm-assign-review-gate.md) — PM review gate 詳細
- [`complete_task.py`](../../skills/platform/asana-buddy/optional/complete_task.py) — 【レビュー】/【承認】はエージェント complete 禁止（exit 3）
