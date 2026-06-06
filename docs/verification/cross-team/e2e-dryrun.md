# E2E ドライラン記録（v3）

## スコープ（現行）

| 段階 | 確認内容 |
|------|----------|
| intake | workflow-orchestrator → bootstrap Handoff |
| bootstrap | asana-buddy → 親 + 企画子 |
| dispatch | task-dispatcher → planning-pm |
| planning-delivery | Handoff → review → gate → Asana タスク化 |

手順: [`docs/e2e/default-workflow.md`](../e2e/default-workflow.md)

## 中間成果物（パス）

| 段階 | ファイル |
|------|----------|
| 設計 | `docs/inventory/skills-inventory.md` |
| I/O | `docs/design/workflow-io-contract.md` |
| セッション | `docs/design/workflow-session-io.md` |
| registry | `workflows/agent-registry.yaml` |
| workflow | `workflows/default.yaml` v3 |
| review 契約 | `docs/design/plan-reviewer-contract.md` |
| E2E 手順 | `docs/e2e/default-workflow.md` |

## 拡張スモーク（registry）

- 未登録 slug 参照時、orchestrator SKILL は registry 更新手順を返す（[`workflow-orchestrator/SKILL.md`](../../skills/platform/workflow-orchestrator/SKILL.md)）

## 結果

- ルート README → intake 起点の **v3** 手順で再現可能
- `handoff_to_asana.py --require-review-result` で review ゲートを CLI 強制可能

## 最新 dryrun 記録

- 全チーム E2E: [`all-teams-dryrun.md`](all-teams-dryrun.md)
- 企画チーム L3 化: [`planning-dept-v3-dryrun.md`](../planning/planning-dept-v3-dryrun.md)
- 索引: [`README.md`](README.md)

## 履歴（v2）

v2 記録: [`archive/default-v2-dryrun.md`](archive/default-v2-dryrun.md) · intake v2: [`archive/orchestrator-intake-v2-dryrun.md`](archive/orchestrator-intake-v2-dryrun.md)
