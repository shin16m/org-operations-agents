# task-dispatcher 実行ガイド — O-Sanpo Loop エピック

Asana 投入後、各子タスクを **task-dispatcher** 経由で開発課へ配賦する。

## Asana 投入（gate 通過後）

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\handoff_to_asana.py `
  --handoff .\work\handoff.osanpo-loop.json `
  --require-review-result .\work\plan-review.osanpo-loop.json `
  -y --if-not-exists
```

## 子タスクごとの dispatch（例）

```
DispatchRequest: task_gid=<子GID>, department=development, parent_gid=<親GID>
organizations.yaml に従い product-manager 用 prompt_snippet を返してください。
```

### サブタスク 1 — 要件定義

```
product-manager として子タスク「【1/4・要件】O-Sanpo Loop 要件定義書」を進めてください。
doc-writer に委譲し docs/requirements/osanpo-loop-requirements.md を完成させてください。
```

### サブタスク 2 — 詳細仕様

```
product-manager: 子「【2/4・設計】O-Sanpo Loop 詳細仕様・API設計」。
docs/specs/osanpo-loop-spec.md を doc-writer で作成してください。
```

### サブタスク 3 — 実装

```
developer: docs/specs/osanpo-loop-spec.md に従い apps/osanpo-loop/ を実装し、reviewer へコードレビューを依頼してください。
```

### サブタスク 4 — README・検証

```
reviewer: apps/osanpo-loop/README.md と主要フローの動作確認を行い、product-manager へ完了報告してください。
```

## Asana GID（投入済み 2026-05-18）

| 種別 | GID | URL |
|------|-----|-----|
| 親エピック | `1214878154566903` | https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1214878154566903 |
| 子【4/4】README・検証 | `1214877047556910` | — |
| 子【3/4】実装 | `1214879364151982` | — |
| 子【2/4】設計 | `1214873900995230` | — |
| 子【1/4】要件 | `1214878981785128` | — |

着手順は **【1/4】→【2/4】→【3/4】→【4/4】**（Asana 上は下から上）。

### 次の dispatch 例（実装タスク）

```
DispatchRequest: task_gid=1214879364151982, department=development, parent_gid=1214878154566903
```

## 完了状態（2026-05-18 同期済み）

以下を実行し、子【1/4】〜【4/4】および親エピックを Asana 上で完了にした。

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\sync_handoff_epic.py `
  --handoff .\work\handoff.osanpo-loop.json `
  --parent 1214878154566903 `
  --complete-through 4 `
  --complete-only

.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\complete_task.py --gid 1214878154566903 -y
```

| タスク | GID | Asana |
|--------|-----|-------|
| 親エピック | `1214878154566903` | 完了 |
| 子【1/4】要件 | `1214878981785128` | 完了 |
| 子【2/4】設計 | `1214873900995230` | 完了 |
| 子【3/4】実装 | `1214879364151982` | 完了 |
| 子【4/4】README | `1214877047556910` | 完了 |
