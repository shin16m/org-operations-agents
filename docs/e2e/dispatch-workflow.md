# 配賦 E2E（default v3 · execution 系 dispatch）

`workflows/with-dispatch.yaml`（ファイル版 v2）で定義される **企画完了後の execution 系子配賦**手順。標準パイプラインは default **v3**（[`workflow-io-contract.md`](../design/workflow-io-contract.md)）。

## 前提

- [`default-workflow.md`](default-workflow.md) で企画チームが完了し、親 + execution 系子が Asana に存在
- 子の notes に `チーム: development` / `チーム: ux` / `チーム: analysis` がある（企画チームが `handoff_to_asana.py` 投入時に `チーム:` 行として付与）
- `department` 未指定時は task-dispatcher が notes の `チーム:` 行または `organizations.yaml` の `pillar_defaults` で推定（Handoff JSON ファイルは読まない）

## 配賦順序

1. **企画子** — intake 直後（`department=planning`）→ [`planning-delivery`](../../workflows/planning-delivery.yaml)
2. **execution 系子** — 企画完了後 → **ux（Web・UI 先行）** → development / analysis

## 1. 未完了子の確認

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <PARENT_GID> --list-subtasks
```

## 2. dispatch — task-dispatcher

自然言語例（開発チーム）:

```
子タスク GID <CHILD_GID> を development に配賦し、開発チーム workflow を起動してください。
```

エージェントは `DispatchRequest` を組み立て、[`task-dispatcher`](../../skills/platform/task-dispatcher/SKILL.md) で entry 用 prompt_snippet を得る。**snippet は [`dispatch-prompt-ssot.md`](../design/dispatch-prompt-ssot.md) から生成すること。**

| department | entry | workflow |
|------------|-------|----------|
| planning | planning-pm | planning-delivery |
| development | product-manager | development-delivery |
| ux | ux-pm | ux-delivery |
| analysis | analytics-pm | analysis-delivery |

## 3. 企画チーム — planning-pm

初回 dispatch（企画子）の詳細は [`default-workflow.md`](default-workflow.md) §3 を参照。

Handoff → review → gate → Asana タスク化 → `DeptWorkComplete`

## 4. UX チーム — ux-pm

[`workflows/ux-delivery.yaml`](../../workflows/ux-delivery.yaml) v2:

Figma UI（ux-designer）→ design_quality（ux-reviewer）→ Design System（design-system-owner）→ ux_spec（ux-reviewer）→ `DeptWorkComplete`（Figma URL + artifacts 公開）

Web Epic では **UI 系 development 子より先**に完了させる。

運用: [`docs/design/ux-delivery-io.md`](../design/ux-delivery-io.md)

## 5. 開発チーム — product-manager

[`workflows/development-delivery.yaml`](../../workflows/development-delivery.yaml) v3。**intake 最初の 1 手は必ず `pm_assign_subtasks`。** PM は worker 成果物を書かない。

起動文 SSOT: [`dispatch-prompt-ssot.md`](../design/dispatch-prompt-ssot.md#development) · 委譲: [`development-pm-assignment.md`](../design/development-pm-assignment.md)

PM（profile 決定・サブタスク分解）→ 各 worker サブ → … → `DeptWorkComplete`

`profile: full-ui` は notes の `## 依存` に UX artifact 必須。

## 6. 子タスク完了（必須）

**ローカル作業が終わったら、署名コメントを残してから Asana を完了にする。** `DeptWorkComplete` や利用者報告の前に実行する。

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py --gid <CHILD_GID> --agent <slug> --skill skills/<organization>/<slug>/SKILL.md --summary "..." --body "..." -y
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\complete_task.py --gid <CHILD_GID> -y
```

詳細: [`docs/design/agent-asana-comment-signature.md`](../design/agent-asana-comment-signature.md)

同一エピックで【1/N】…【N/N】まで連続完了した場合（Handoff の `【n/m】` タイトルが付いているとき）:

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\sync_handoff_epic.py `
  --handoff .\output\planning\handoff\<theme>.json `
  --parent <PARENT_GID> `
  --complete-through N `
  --complete-only
```

## 7. エピック完了

1. `fetch_task.py --gid <PARENT_GID> --list-subtasks` で未完了子が無いことを確認
2. （推奨）親エピックを `complete_task.py --gid <PARENT_GID> -y` で完了
3. **workflow-orchestrator** が利用者へエピック完了を報告

未完了の子が残ったまま「完了しました」と報告しない。

## 分析チーム

`department=analysis` の子は [`workflows/analysis-delivery.yaml`](../../workflows/analysis-delivery.yaml) v2 へルーティング（entry: **analytics-pm**）。

自然言語例:

```
子タスク GID <CHILD_GID> を analysis に配賦し、分析チーム workflow を起動してください。
```

フェーズ概要（profile により出し分け）: analytics-requirements-writer（要件）→ データ設計 → ETL → 品質 → 探索 → モデル → **本番ゲート** → デプロイ → release。`model-serve` / `insights` / `catalog` / `lite` は [`analytics-pm-assignment.md`](../design/analytics-pm-assignment.md) 参照。

運用ルール: [`docs/design/analysis-delivery-io.md`](../design/analysis-delivery-io.md)

Handoff 例: [`handoff.analysis-delivery.json`](../../skills/planning/issue-story-planner/examples/handoff.analysis-delivery.json)
