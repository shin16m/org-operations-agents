# 配賦 E2E（with-dispatch v2）

default v3 で企画完了（Handoff Asana 投入）後、**execution 系子タスク 1 件ごと**にチームへ配賦する手順。

## 前提

- [`default-workflow.md`](default-workflow.md) で企画チームが完了し、親 + execution 系子が Asana に存在
- 子の notes に `チーム: development` / `チーム: analysis` がある（企画チームが `handoff_to_asana.py` 投入時に `チーム:` 行として付与）
- `department` 未指定時は task-dispatcher が notes の `チーム:` 行または `organizations.yaml` の `pillar_defaults` で推定（Handoff JSON ファイルは読まない）

## 配賦順序

1. **企画子** — intake 直後（`department=planning`）→ [`planning-delivery`](../../workflows/planning-delivery.yaml)
2. **execution 系子** — 企画完了後 → development / analysis

## 1. 未完了子の確認

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <PARENT_GID> --list-subtasks
```

## 2. dispatch — task-dispatcher

自然言語例（開発チーム）:

```
子タスク GID <CHILD_GID> を development に配賦し、開発チーム workflow を起動してください。
```

エージェントは `DispatchRequest` を組み立て、[`task-dispatcher`](../../skills/platform/task-dispatcher/SKILL.md) で entry 用 prompt_snippet を得る。

| department | entry | workflow |
|------------|-------|----------|
| planning | planning-pm | planning-delivery |
| development | product-manager | development-delivery |
| analysis | analytics-pm | analysis-delivery |

## 3. 企画チーム — planning-pm

初回 dispatch（企画子）の詳細は [`default-workflow.md`](default-workflow.md) §3 を参照。

Handoff → review → gate → Asana タスク化 → `DeptWorkComplete`

## 4. 開発チーム — product-manager

[`workflows/development-delivery.yaml`](../../workflows/development-delivery.yaml) に従い:

要件定義（doc-writer）→ レビュー → 開発（developer）→ レビュー・検証 → 詳細仕様（doc-writer）→ 整合レビュー → `DeptWorkComplete`

## 5. 子タスク完了（必須）

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

## 6. エピック完了

1. `fetch_task.py --gid <PARENT_GID> --list-subtasks` で未完了子が無いことを確認
2. （推奨）親エピックを `complete_task.py --gid <PARENT_GID> -y` で完了
3. **workflow-orchestrator** が利用者へエピック完了を報告

未完了の子が残ったまま「完了しました」と報告しない。

## 分析チーム

`department=analysis` の子は [`workflows/analysis-delivery.yaml`](../../workflows/analysis-delivery.yaml) へルーティング（entry: **analytics-pm**）。

自然言語例:

```
子タスク GID <CHILD_GID> を analysis に配賦し、分析チーム workflow を起動してください。
```

フェーズ概要: 要求定義 → データ設計 → ETL → 品質 → 探索 → モデル → **本番ゲート** → デプロイ → 価値検証。

運用ルール: [`docs/design/analysis-delivery-io.md`](../design/analysis-delivery-io.md)

Handoff 例: [`handoff.analysis-delivery.json`](../../skills/planning/issue-story-planner/examples/handoff.analysis-delivery.json)

## 過渡期

単一 `task-executor` は [`default-workflow.md`](default-workflow.md#オプション-work--サブタスク実行deprecated) を参照。
