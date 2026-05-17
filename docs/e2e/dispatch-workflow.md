# 配賦・開発課 E2E（with-dispatch）

企画（default v2）のあと、**子タスク 1 件ごと**に課へ配賦する手順。

## 前提

- [`default-workflow.md`](default-workflow.md) で親+子が Asana に存在
- 子の notes に `課: development` がある、または Handoff v1.2 の `department`

## 1. 未完了子の確認

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\fetch_task.py --gid <PARENT_GID> --list-subtasks
```

## 2. dispatch — task-dispatcher

自然言語例:

```
子タスク GID <CHILD_GID> を development に配賦し、開発課 workflow を起動してください。
```

エージェントは `DispatchRequest` を組み立て、[`task-dispatcher`](../../skills/task-dispatcher/SKILL.md) で `product-manager` 用 prompt_snippet を得る。

## 3. 開発課 — product-manager

[`workflows/development-delivery.yaml`](../../workflows/development-delivery.yaml) に従い:

要件定義（doc-writer）→ レビュー → 開発（developer）→ レビュー・検証 → 詳細仕様（doc-writer）→ 整合レビュー → `DeptWorkComplete`

## 4. 子タスク完了（必須）

**ローカル作業が終わったら、署名コメントを残してから Asana を完了にする。** `DeptWorkComplete` や利用者報告の前に実行する。

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\comment_task.py --gid <CHILD_GID> --agent <slug> --skill skills/<slug>/SKILL.md --summary "..." --body "..." -y
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\complete_task.py --gid <CHILD_GID> -y
```

詳細: [`docs/design/agent-asana-comment-signature.md`](../design/agent-asana-comment-signature.md)

同一エピックで【1/N】…【N/N】まで連続完了した場合（Handoff の `【n/m】` タイトルが付いているとき）:

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\sync_handoff_epic.py `
  --handoff .\work\handoff.<theme>.json `
  --parent <PARENT_GID> `
  --complete-through N `
  --complete-only
```

## 5. エピック完了

1. `fetch_task.py --gid <PARENT_GID> --list-subtasks` で未完了子が無いことを確認
2. （推奨）親エピックを `complete_task.py --gid <PARENT_GID> -y` で完了
3. **workflow-orchestrator** が利用者へエピック完了を報告

未完了の子が残ったまま「完了しました」と報告しない。

## 分析課

`department=analysis` は [`organizations.yaml`](../../workflows/organizations.yaml) で `enabled: false`（プレースホルダ）。

## 過渡期

単一 `task-executor` は [`with-execution.md`](default-workflow.md#オプション-work--サブタスク実行) を参照。
