# 企画チーム L3 化 — スモークチェックリスト

組織構成変更（default v3）後の文書・registry 整合確認。

## registry / workflow

- [x] `workflows/agent-registry.yaml` に `planning-pm` が `dept_orchestrate` で登録
- [x] `issue-story-planner` が `dept_work`、`plan-reviewer` が `dept_review`
- [x] `workflows/default.yaml` version `"3"`: intake → bootstrap → dispatch
- [x] `workflows/planning-delivery.yaml` が存在
- [x] `workflows/organizations.yaml` planning → `planning-delivery` / `planning-pm`

## スキル

- [x] `skills/planning/planning-pm/SKILL.md` が存在
- [x] `workflow-orchestrator` / `task-dispatcher` / `asana-buddy` が v3 フローを記述
- [x] `issue-story-planner` / `plan-reviewer` が planning-pm 委譲を記述

## ドキュメント

- [x] [`docs/e2e/default-workflow.md`](../e2e/default-workflow.md) が v3 手順
- [x] [`docs/inventory/skills-inventory.md`](../inventory/skills-inventory.md) に planning-pm
- [x] [`docs/design/planning-delivery-io.md`](../design/planning-delivery-io.md)
- [x] [`.cursor/rules/workflow-intake-required.mdc`](../../.cursor/rules/workflow-intake-required.mdc) が v3

## ドライラン（2026-05-23）

- [x] bootstrap Handoff 保存
- [x] bootstrap Asana 投入（親 + 企画子）
- [x] Handoff + PlanReviewResult 保存
- [x] planning-pm 署名コメント → 企画子 complete
- [x] execution 系子 dispatch（開発チーム）— 2026-05-23 完了
- [x] チーム表記 dry-run（`チーム:` 書込 / legacy `課:` 読取）— 2026-05-23

記録: [`planning-dept-v3-dryrun.md`](planning-dept-v3-dryrun.md)

## 関連

- E2E: [`default-workflow.md`](../e2e/default-workflow.md)
- 組織モデル: [`org-dispatch-model.md`](../design/org-dispatch-model.md)
