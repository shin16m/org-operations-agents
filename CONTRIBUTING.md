# CONTRIBUTING

## 新エージェント追加（必須 3 ステップ）

1. **`agent-creater`** — Copilot/Cursor で問診し、`skills/<slug>/` の README / SKILL / personas 雛形を生成・保存する。他スキルでフォルダを手書きしない。
2. **registry** — [`workflows/agent-registry.yaml`](workflows/agent-registry.yaml) に slug・slot・I/O 参照・`enabled` を追加する。
3. **workflow** — [`workflows/default.yaml`](workflows/default.yaml)（または別 workflow ファイル）に段階・`agent` 参照を追加する。

PR では [`docs/design/workflow-io-contract.md`](docs/design/workflow-io-contract.md) のゲート・境界に抵触しないか確認する。

## スキル変更

- I/O 破壊的変更は Handoff `schema_version` と schema JSON を更新する。
- Asana サブタスク順: JSON は着手順（先頭＝最初）、API は [`asana-buddy` SKILL](skills/asana-buddy/SKILL.md) の逆順作成。

## レガシー

`skills/agent-creater/agents/` 配下は配置しない。正は `skills/<slug>/`。

## ワークフロー運用

- 標準 workflow（v2）の入口は **`workflow-orchestrator`（intake）**。順序: intake → plan → review → gate → execute（[`workflows/default.yaml`](workflows/default.yaml)）。
- **`plan-reviewer` による review は必須**。Handoff を Asana に載せる前に `PlanReviewResult`（`passed` / `passed_with_notes`）を得ること。
- **Asana 投入（CI・本番）:** `handoff_to_asana.py` には `--require-review-result` を付与する（review JSON なしでは CLI が失敗する）。
- **エージェント作業の可視化:** タスク完了前に [`comment_task.py`](skills/asana-buddy/optional/comment_task.py) で **agent slug + skill パス**の署名付きコメントを投稿する（[`docs/design/agent-asana-comment-signature.md`](docs/design/agent-asana-comment-signature.md)）。その後 `complete_task.py`。
- **移行:** 以前 issue-story-planner 先頭で運用していた場合も、**新規依頼は orchestrator（intake）から**開始する。

## 検証

- E2E: [`docs/e2e/default-workflow.md`](docs/e2e/default-workflow.md)
- 記録例: [`docs/verification/e2e-dryrun.md`](docs/verification/e2e-dryrun.md)
