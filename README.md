# org-operations-agents

**組織運用エージェントテンプレート** — `agent-creater`（エージェント生成）と **6 チーム**構成の org runtime（intake → plan → Asana → dispatch · 監査チーム含む）を同梱。fork して拡張する。

Git で共有する **Cursor / Copilot 用エージェントスキル**・宣言的 workflow・Asana 連携の SSOT。

> **スコープ:** 本リポジトリは **汎用の組織運用テンプレート**（Git で fork して誰でも利用可）。エピック成果物（要件・コード・モデル等）は **`output/` に書くが git 管理しない**（[`docs/design/artifact-policy.md`](docs/design/artifact-policy.md)）。**プロダクト固有の運用変更・assign plan 実行版はローカルの `output/` / `work/` のみ**で行う。製品ソースは別リポジトリ。

## レイアウト

| パス | 内容 |
|------|------|
| [`skills/`](skills/) | エージェント定義（統括グループ / 企画 / 開発 / 分析 / UX / **組織改善** `governance` / **監査** `audit`）+ 各 `personas/` |
| [`output/`](output/) | 実行時ワークスペース（**git 管理外**・フォルダテンプレのみ） |
| [`work/`](work/) | PM assign plan 等の実行時作業領域 |
| [`workflows/`](workflows/) | 宣言的 workflow |
| [`docs/`](docs/) | 設計・E2E・検証（契約文書） |

組織モデル: [`docs/design/department-model.md`](docs/design/department-model.md) · スキル・ペルソナ: [`docs/design/skill-persona-principles.md`](docs/design/skill-persona-principles.md)

## スキル一覧

| スキル | 役割 |
|--------|------|
| [`agent-creater`](skills/platform/agent-creater/SKILL.md) | **新規** `skills/<organization>/<slug>/` の唯一の生成入口 |
| [`workflow-orchestrator`](skills/platform/workflow-orchestrator/SKILL.md) | **課題の入口（intake）** と bootstrap / dispatch 委譲 |
| [`planning-pm`](skills/planning/planning-pm/SKILL.md) | 企画チーム PM（Handoff → review → gate → Asana タスク化） |
| [`issue-story-planner`](skills/planning/issue-story-planner/SKILL.md) | 課題 → ストーリー → Handoff v1.1 |
| [`plan-reviewer`](skills/planning/plan-reviewer/SKILL.md) | Handoff の品質・リスクレビュー |
| [`asana-buddy`](skills/platform/asana-buddy/SKILL.md) | Handoff → Asana タスク |
| [`task-dispatcher`](skills/platform/task-dispatcher/SKILL.md) | 子タスクをチームへ配賦（dispatch） |
| [`product-manager`](skills/development/product-manager/SKILL.md) | 開発チーム PM（子 1 件のハブ） |
| [`ux-pm`](skills/ux/ux-pm/SKILL.md) | UX チーム PM |
| [`ux-designer`](skills/ux/ux-designer/SKILL.md) / [`design-system-owner`](skills/ux/design-system-owner/SKILL.md) / [`ux-reviewer`](skills/ux/ux-reviewer/SKILL.md) | UX チーム委譲ロール（Figma-first v2） |
| [`requirements-writer`](skills/development/requirements-writer/SKILL.md) / [`tech-designer`](skills/development/tech-designer/SKILL.md) / [`developer`](skills/development/developer/SKILL.md) / [`dev-reviewer`](skills/development/dev-reviewer/SKILL.md) / [`qa-verifier`](skills/development/qa-verifier/SKILL.md) | 開発チーム委譲ロール |
| [`analytics-pm`](skills/analysis/analytics-pm/SKILL.md) | 分析チーム PM（profile · 子 1 件のハブ） |
| [`analytics-requirements-writer`](skills/analysis/analytics-requirements-writer/SKILL.md) / [`data-architect`](skills/analysis/data-architect/SKILL.md) / [`data-engineer`](skills/analysis/data-engineer/SKILL.md) / [`data-steward`](skills/analysis/data-steward/SKILL.md) / [`data-analyst`](skills/analysis/data-analyst/SKILL.md) / [`data-scientist`](skills/analysis/data-scientist/SKILL.md) / [`ml-engineer`](skills/analysis/ml-engineer/SKILL.md) / [`analysis-reviewer`](skills/analysis/analysis-reviewer/SKILL.md) | 分析チームの委譲ロール（v2） |
| [`audit-pm`](skills/audit/audit-pm/SKILL.md) | 監査チーム PM（組織変更エピックの L3 統制） |
| [`consistency-auditor`](skills/audit/consistency-auditor/SKILL.md) / [`audit-reviewer`](skills/audit/audit-reviewer/SKILL.md) | 監査チーム委譲ロール |
| [`governance-pm`](skills/governance/governance-pm/SKILL.md) | 組織改善チーム PM（org-meta SSOT 変更） |
| [`ssot-implementer`](skills/governance/ssot-implementer/SKILL.md) / [`governance-reviewer`](skills/governance/governance-reviewer/SKILL.md) | 組織改善チーム委譲ロール |

## 標準 workflow（default v3）

パイプライン図・段階定義の SSOT: [`docs/design/workflow-io-contract.md`](docs/design/workflow-io-contract.md)

- **入口:** `workflow-orchestrator`（intake）に生課題を渡す
- **企画:** `planning-pm` ハブが Handoff → review → gate → Asana 投入を担当
- **review:** `plan-reviewer` は省略不可（人間目視のみでは `review_passed` にならない）
- **gate:** `planning-pm` が Handoff 要約提示後、人間承認を取得

手順: [`docs/e2e/default-workflow.md`](docs/e2e/default-workflow.md) · YAML: [`workflows/default.yaml`](workflows/default.yaml) v3 · 企画: [`workflows/planning-delivery.yaml`](workflows/planning-delivery.yaml)

### 移行

以前は issue-story-planner 先頭だった。**新規依頼は orchestrator（intake）から**開始する（詳細: [`CONTRIBUTING.md`](CONTRIBUTING.md)）。

## セットアップ

```powershell
.\skills\platform\asana-buddy\optional\setup_venv.ps1
```

`skills/platform/asana-buddy/optional/.env.example` を `optional/.env` にコピーして値を設定（`.env` は gitignore）:

```powershell
Copy-Item .\skills\platform\asana-buddy\optional\.env.example .\skills\platform\asana-buddy\optional\.env
```

## クイックスタート（Asana 投入）

1. [`workflow-orchestrator`](skills/platform/workflow-orchestrator/README.md)（**intake**）に課題を渡す → bootstrap → dispatch（企画チーム）  
   **intake-asana:** Asana タスク URL/GID も可（[`intake_from_asana.py`](tools/intake_from_asana.py) · [`workflow-orchestrator/SKILL.md`](skills/platform/workflow-orchestrator/SKILL.md) 起動例 C）
2. [`planning-pm`](skills/planning/planning-pm/SKILL.md) が [`issue-story-planner`](skills/planning/issue-story-planner/SKILL.md) で Handoff JSON を得る
3. **必須:** [`plan-reviewer`](skills/planning/plan-reviewer/SKILL.md) で `PlanReviewResult`（`passed` / `passed_with_notes`）
4. [`planning-pm`](skills/planning/planning-pm/SKILL.md)（**gate**）で Asana 投入承認
5. [`handoff_to_asana.py`](skills/platform/asana-buddy/optional/handoff_to_asana.py) で投入（**review 強制**）:

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\handoff_to_asana.py `
  --handoff .\path\to\handoff.json `
  --require-review-result .\path\to\review.json `
  -y --if-not-exists
```

`--require-review-result` を省略すると SKILL 上の前提のみ（CI・本番運用では付与を推奨。詳細: [`CONTRIBUTING.md`](CONTRIBUTING.md)）。

詳細: [`docs/e2e/default-workflow.md`](docs/e2e/default-workflow.md)

### タスク化のあと（配賦・各チーム）

企画完了後、execution 系子タスクごとに **dispatch → チーム workflow** が走ります。

```
dispatch → planning-pm → issue-story-planner / plan-reviewer → asana-buddy（Handoff タスク化）
dispatch → ux-pm → ux-designer / design-system-owner / ux-reviewer
dispatch → product-manager → requirements-writer / tech-designer / developer / dev-reviewer / qa-verifier（full-ui 時 ux-reviewer も）
dispatch → analytics-pm → data-architect / … / analysis-reviewer
dispatch → governance-pm → ssot-implementer / governance-reviewer（org-meta）
dispatch → audit-pm → consistency-auditor / audit-reviewer（組織変更時・execution 系の最後）
```

- 企画チーム: [`workflows/planning-delivery.yaml`](workflows/planning-delivery.yaml)
- 開発チーム: [`workflows/development-delivery.yaml`](workflows/development-delivery.yaml) v3
- UX チーム: [`workflows/ux-delivery.yaml`](workflows/ux-delivery.yaml)
- 分析チーム: [`workflows/analysis-delivery.yaml`](workflows/analysis-delivery.yaml)

- 推奨: [`workflows/with-dispatch.yaml`](workflows/with-dispatch.yaml) · [`docs/e2e/dispatch-workflow.md`](docs/e2e/dispatch-workflow.md)

## エピック進行

- 基盤構築: [`handoff.agent-workflow-orchestration.json`](skills/planning/issue-story-planner/examples/handoff.agent-workflow-orchestration.json)
- オーケストレーター入口化: [`handoff.orchestrator-intake-entry.json`](skills/planning/issue-story-planner/examples/handoff.orchestrator-intake-entry.json)
- 組織配賦・PM ワークフロー: [`handoff.org-dispatch-pm-workflow.json`](skills/planning/issue-story-planner/examples/handoff.org-dispatch-pm-workflow.json)
- 分析チーム delivery: [`handoff.analysis-delivery.json`](skills/planning/issue-story-planner/examples/handoff.analysis-delivery.json)

棚卸し: [`docs/inventory/skills-inventory.md`](docs/inventory/skills-inventory.md)

## 貢献

[`CONTRIBUTING.md`](CONTRIBUTING.md)
