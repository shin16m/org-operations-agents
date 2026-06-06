# CONTRIBUTING

## 新エージェント追加（必須 6 ステップ · v2 基準）

1. **`agent-creater`** — `skills/<organization>/<slug>/` の README / SKILL / `personas/<slug>.md`（**志向** 必須）を生成。他スキルでフォルダを手書きしない。
2. **registry** — [`workflows/agent-registry.yaml`](workflows/agent-registry.yaml) に slug · slot · I/O · `enabled: true`。
3. **workflow** — 所属レイヤに応じて更新:
   - L1 統括（platform）— [`workflows/default.yaml`](workflows/default.yaml) または [`workflows/with-dispatch.yaml`](workflows/with-dispatch.yaml)
   - L3 チーム worker — `workflows/<dept>-delivery.yaml` + 該当 `*-pm-assignment.md` + assign plan 例
4. **対応表** — [`docs/inventory/skill-persona-matrix.md`](docs/inventory/skill-persona-matrix.md) に 1 行追加。
5. **棚卸し** — [`docs/inventory/skills-inventory.md`](docs/inventory/skills-inventory.md) · [`workflows/agent-display-names.yaml`](workflows/agent-display-names.yaml)
6. **検証（PR 前）:**

```powershell
python tools/check_new_skill.py --slug <新slug> --department <dept>
python tools/validate_org_registry.py
```

設計原則: [`docs/design/skill-persona-principles.md`](docs/design/skill-persona-principles.md) · 強みの型: [`docs/design/delivery-strength-pattern.md`](docs/design/delivery-strength-pattern.md)

## 新チーム追加（必須 4 点セット + チェックリスト）

[`docs/design/department-model.md`](docs/design/department-model.md) に従う:

1. [`workflows/organizations.yaml`](workflows/organizations.yaml) — `departments[]` に 1 行
2. `workflows/<id>-delivery.yaml` — チーム内 workflow
3. `docs/design/<id>-delivery-io.md` — チーム内 I/O + チーム間 I/O
4. PM ハブ — `skills/<dept>/<dept>-pm/`（`agent-creater` で生成可）

**漏れ防止:** [`docs/design/new-department-checklist.md`](docs/design/new-department-checklist.md) の A〜J を確認。

**機械検証（PR 前）:**

```powershell
python tools/validate_org_registry.py
python tools/validate_ssot_contract.py
python tools/validate_fixture_schemas.py
python tools/check_new_department.py --department <id>
python tools/check_new_department.py --all
python tools/check_new_skill.py --all-enabled
```

PR では [`.github/workflows/validate.yml`](.github/workflows/validate.yml) が上記を実行する。

**チーム取り決め一覧:** [`team-conventions.md`](docs/design/team-conventions.md) · 組織: [`department-model.md`](docs/design/department-model.md)

### L3 delivery を開発 v3 型で揃える場合

[`docs/design/delivery-strength-pattern.md`](docs/design/delivery-strength-pattern.md) のチェックリストに加え:

- `docs/design/<dept>-pm-assignment.md`（profile · `human_review_gate` opt-in · pm_assign 必須）
- `skills/<dept>/examples/assign-plan*.json`
- `docs/verification/*<dept>*dryrun*.md` または `tools/run_*dryrun*.py`
- 下流がある場合: [`cross-team-artifact-bridge.md`](docs/design/cross-team-artifact-bridge.md) + Handoff 例

## スキル変更

- I/O 破壊的変更は Handoff `schema_version` と schema JSON を更新する。
- Asana サブタスク順: JSON は着手順（先頭＝最初）、API は [`asana-buddy` SKILL](skills/platform/asana-buddy/SKILL.md) の逆順作成。

## レガシー

`skills/<organization>/<slug>/` 以外（旧フラット `skills/<slug>/` や `agent-creater/agents/`）には配置しない。組織一覧は [`skills/README.md`](skills/README.md)。

## ワークフロー運用

- 標準 workflow（v3）の入口は **`workflow-orchestrator`（intake）**。パイプライン全体: [`docs/design/workflow-io-contract.md`](docs/design/workflow-io-contract.md) · 手順: [`docs/e2e/default-workflow.md`](docs/e2e/default-workflow.md)
- **`plan-reviewer` による review は必須**（planning-delivery 内）。Handoff を Asana に載せる前に `PlanReviewResult` を得ること。
- **Asana 投入（CI・本番）:** `handoff_to_asana.py` には `--require-review-result` を付与する。
- **エージェント作業の可視化:** タスク完了前に [`comment_task.py`](skills/platform/asana-buddy/optional/comment_task.py) で **agent slug + skill パス**の署名付きコメントを投稿する（[`docs/design/agent-asana-comment-signature.md`](docs/design/agent-asana-comment-signature.md)）。その後 `complete_task.py`。
- **移行:** 新規依頼は orchestrator（intake）から開始する。

## 検証

- E2E: [`docs/e2e/default-workflow.md`](docs/e2e/default-workflow.md)
- 記録例: [`docs/verification/README.md`](docs/verification/README.md)
