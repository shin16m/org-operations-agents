# task-executor SKILL

**独立スキル:** Asana 上の**既存サブタスク**を読み、`done_when` に沿ってリポジトリ内作業を行い、完了を報告する（`work` スロット）。

> **Deprecated:** 新規依頼は [`with-dispatch.yaml`](../../workflows/with-dispatch.yaml) → [`task-dispatcher`](../task-dispatcher/SKILL.md) → 課 workflow（開発課は [`product-manager`](../product-manager/SKILL.md)）を使用する。本スキルは過渡期の単一ワーカーとして残す。

人間向け: [`README.md`](README.md) · I/O: [`docs/design/task-work-io.md`](../../docs/design/task-work-io.md) · 境界: [`docs/design/task-execution-boundary.md`](../../docs/design/task-execution-boundary.md)

## 前提

- タスクは [`asana-buddy`](../asana-buddy/SKILL.md) の execute 段階で**既に作成済み**
- タスク内容の取得: `skills/asana-buddy/optional/fetch_task.py --gid <GID>`
- 署名コメント: `skills/asana-buddy/optional/comment_task.py`（`--agent task-executor`）
- 完了マーク: `skills/asana-buddy/optional/complete_task.py --gid <GID> -y`（**コメントの後**）

## 責務

1. `TaskWorkRequest` または利用者指定の **task_gid** を受け取る
2. Asana `notes`（背景・概要・完了条件）を読み、作業計画を短く示す
3. リポジトリ内の実装・文書更新を行う（Cursor / エージェント実行）
4. `done_when` を満たしたと判断したら `TaskWorkResult`（`status: completed`）を出力し、`complete_task.py --gid <GID> -y` を**実行してよい**（人間の追加確認は不要）

## やらないこと

- `AsanaBuddyHandoff` の**新規作成**（→ issue-story-planner）
- 親タスク＋子の**一括作成**（→ asana-buddy / handoff_to_asana.py）
- 新規 `skills/<slug>/` の生成（→ **agent-creater**）
- plan / review の代替

## 新規ツールが要る場合

`status: needs_tool` とし、`delegated_to: agent-creater` を明記。agent-creater 完了後に本スキルへ再開。

## 起動例

```
次の Asana サブタスクを実行してください。GID: 〈task_gid〉
fetch_task.py で内容を確認し、done_when を満たすまで作業し、TaskWorkResult を返してください。
```

## 出力（モデル向け）

- `TaskWorkResult` JSON 1 ブロック（[`task-work-io.md`](../../docs/design/task-work-io.md)）
- 変更ファイル一覧（`artifacts`）
- 完了時: `comment_task.py` → `complete_task.py -y`（`done_when` 未達のときは完了しない）

スキーマ: [`schemas/task-work-result.v1.schema.json`](schemas/task-work-result.v1.schema.json)
