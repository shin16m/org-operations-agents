# E2E ドライラン記録

タスク 11 成果物。

## 実施日

2026-05-17（エピック実装セッション）

## スコープ

- リポジトリ内ドキュメント・スキル・workflow/registry の整合確認
- 本エピック Handoff の Asana 投入は実施済み（過去セッション）

## 中間成果物（パス）

| 段階 | ファイル |
|------|----------|
| 設計 | `docs/inventory/skills-inventory.md` |
| I/O | `docs/design/workflow-io-contract.md` |
| registry | `workflows/agent-registry.yaml` |
| workflow | `workflows/default.yaml` |
| review 契約 | `docs/design/plan-reviewer-contract.md` |
| Handoff 参照 | `skills/issue-story-planner/examples/handoff.agent-workflow-orchestration.json` |
| E2E 手順 | `docs/e2e/default-workflow.md` |

## Asana

- 親エピック: https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1214879346897459

## 拡張スモーク（registry）

- `workflows/agent-registry.yaml` に未登録 slug を workflow が参照した場合、orchestrator SKILL は「registry 更新手順」を返す設計（[`workflow-orchestrator/SKILL.md`](../../skills/workflow-orchestrator/SKILL.md)）
- ダミー slug 追加の手順は CONTRIBUTING「新エージェント追加」に記載

## 結果

- タスク 9–10 の README / CONTRIBUTING / SKILL リンクと実ファイルが一致
- 第三者はルート README → venv → `docs/e2e/default-workflow.md` で再現可能
