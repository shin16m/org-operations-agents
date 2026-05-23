# CONTRIBUTING

## 新エージェント追加（必須 3 ステップ）

1. **`agent-creater`** — Copilot/Cursor で問診し、`skills/<organization>/<slug>/` の README / SKILL / personas 雛形を生成・保存する。他スキルでフォルダを手書きしない。
2. **registry** — [`workflows/agent-registry.yaml`](workflows/agent-registry.yaml) に slug・slot・I/O 参照・`enabled` を追加する。
3. **workflow** — [`workflows/default.yaml`](workflows/default.yaml)（または別 workflow ファイル）に段階・`agent` 参照を追加する。

PR では [`docs/design/workflow-io-contract.md`](docs/design/workflow-io-contract.md) のゲート・境界に抵触しないか確認する。

## 新チーム追加（必須 4 点セット + チェックリスト）

[`docs/design/department-model.md`](docs/design/department-model.md) に従う:

1. [`workflows/organizations.yaml`](workflows/organizations.yaml) — `departments[]` に 1 行
2. `workflows/<id>-delivery.yaml` — チーム内 workflow
3. `docs/design/<id>-delivery-io.md` — チーム内 I/O + チーム間 I/O
4. PM ハブ — `skills/<dept>/<dept>-pm/`（`agent-creater` で生成可）

**漏れ防止:** [`docs/design/new-department-checklist.md`](docs/design/new-department-checklist.md) の A〜H を確認。

**機械検証（PR 前）:**

```powershell
python tools/validate_org_registry.py
```

**チーム取り決め一覧:** [`team-conventions.md`](docs/design/team-conventions.md) · 組織: [`department-model.md`](docs/design/department-model.md)

## スキル変更

- I/O 破壊的変更は Handoff `schema_version` と schema JSON を更新する。
- Asana サブタスク順: JSON は着手順（先頭＝最初）、API は [`asana-buddy` SKILL](skills/platform/asana-buddy/SKILL.md) の逆順作成。

## レガシー

`skills/<organization>/<slug>/` 以外（旧フラット `skills/<slug>/` や `agent-creater/agents/`）には配置しない。組織一覧は [`skills/README.md`](skills/README.md)。

## ワークフロー運用

- 標準 workflow（v3）の入口は **`workflow-orchestrator`（intake）**。順序: intake → bootstrap → dispatch → planning-delivery（Handoff → review → gate → Asana）→ execution 系 dispatch（[`workflows/default.yaml`](workflows/default.yaml)）。
- **`plan-reviewer` による review は必須**（planning-delivery 内）。Handoff を Asana に載せる前に `PlanReviewResult` を得ること。
- **Asana 投入（CI・本番）:** `handoff_to_asana.py` には `--require-review-result` を付与する（review JSON なしでは CLI が失敗する）。
- **エージェント作業の可視化:** タスク完了前に [`comment_task.py`](skills/platform/asana-buddy/optional/comment_task.py) で **agent slug + skill パス**の署名付きコメントを投稿する（[`docs/design/agent-asana-comment-signature.md`](docs/design/agent-asana-comment-signature.md)）。その後 `complete_task.py`。
- **移行:** 以前 issue-story-planner 先頭で運用していた場合も、**新規依頼は orchestrator（intake）から**開始する。

## 検証

- E2E: [`docs/e2e/default-workflow.md`](docs/e2e/default-workflow.md)
- 組織 registry 整合: `python tools/validate_org_registry.py`
- 企画チーム v3 スモーク: [`docs/verification/planning-dept-v3-smoke.md`](docs/verification/planning-dept-v3-smoke.md)
- 記録例: [`docs/verification/e2e-dryrun.md`](docs/verification/e2e-dryrun.md)
