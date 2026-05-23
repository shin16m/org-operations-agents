# asana-buddy

Asana にタスクを作成・整理するための **独立スキル** です。課題整理とストーリーは [`issue-story-planner`](../../planning/issue-story-planner/SKILL.md) が担当し、本スキルはその成果（または手元の要件）を Asana の親タスク＋サブタスクとして投入します。

詳細な契約・モデル向け手順は [`SKILL.md`](SKILL.md) を参照してください。

## いつ使うか

- Asana にエピック（親）と作業タスク（子）をまとめて作りたい
- [`issue-story-planner`](../../planning/issue-story-planner/SKILL.md) が出力した **AsanaBuddyHandoff** JSON を Asana に反映したい
- 単発タスクを API で追加したい（確認プロンプト付き）

## フォルダ構成

| パス | 内容 |
|------|------|
| `SKILL.md` | スキル定義・ハンドオフ消費の約束事 |
| `personas/` | Copilot 等用のペルソナ（`asana_buddy.json` / `.md`） |
| `optional/` | Python スクリプト、`requirements.txt`、`setup_venv.ps1` |

## セットアップ

1. リポジトリルートで仮想環境と依存関係を入れる（Windows 例）:

   ```powershell
   .\skills\platform\asana-buddy\optional\setup_venv.ps1
   ```

2. `optional/.env` にトークン等を置く（**コミットしない**）:

   ```env
   ASANA_TOKEN=your_personal_access_token
   ASANA_PROJECT_ID=your_project_gid
   ```

   `ASANA_PROJECT_ID` が無い場合、一部スクリプトはテスト用プロジェクト GID にフォールバックします（stderr に注意が出ます）。

3. プロジェクト GID の確認:

   ```powershell
   .\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\handoff_to_asana.py --list-projects
   ```

## スクリプト一覧

| スクリプト | 用途 |
|------------|------|
| `agent_handler_asana.py` | 単発タスク作成（`-y` で確認スキップ） |
| `handoff_to_asana.py` | **Handoff JSON** から親＋子を作成、または `--if-not-exists` / `--parent` で既存親へ **sync** |
| `fetch_task.py` | タスク読取（PM / ワーカー workflow） |
| `comment_task.py` | **署名付き**エージェント作業コメント（[`agent-asana-comment-signature.md`](../../../docs/design/agent-asana-comment-signature.md)） |
| `complete_task.py` | タスク完了マーク（**comment の後**） |
| `pm_assign_subtasks.py` | PM assign plan JSON からネストサブタスク作成 |
| `sync_handoff_epic.py` | Handoff と Asana 子の照合・一括完了 |
| `update_task_notes.py` | notes 更新（`チーム:` / `担当:` ヘッダ） |
| `asana_delete_task.py` | タスク削除（`-y` 必須） |
| `asana_program_common.py` | 共有: notes 組み立て・プロジェクト解決・逆順サブ作成 |

**一括投入**は `handoff_to_asana.py` を使う（テーマ別 one-off スクリプトはテンプレ repo には含めない）。

## 実行例

**単発タスク**（リポジトリルートがカレント）:

```text
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\agent_handler_asana.py --project <PROJ_GID> --name "タスク名" --notes "メモ" -y
```

**Handoff 投入（重複作成を避ける）**:

```text
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\handoff_to_asana.py --handoff path\to\handoff.json --require-review-result path\to\review.json -y --if-not-exists
```

サブタスクは一覧で **上から順に消化** しやすいよう、API では定義リストの **逆順** で作成します（[`SKILL.md`](SKILL.md) 参照）。

## 標準パイプライン（workflow v3）

1. [`workflow-orchestrator`](../workflow-orchestrator/README.md) — **intake** → bootstrap Handoff → Asana に企画子 1 件
2. [`task-dispatcher`](../task-dispatcher/SKILL.md) — 企画子を **planning-pm**（企画チーム L3）へ dispatch
3. [`planning-pm`](../../planning/planning-pm/SKILL.md) — [`issue-story-planner`](../../planning/issue-story-planner/SKILL.md) → [`plan-reviewer`](../../planning/plan-reviewer/SKILL.md) → **gate**（人間承認）
4. 本スキル — `handoff_to_asana.py --require-review-result`（既存親は **sync**）

詳細: [`docs/e2e/default-workflow.md`](../../../docs/e2e/default-workflow.md)

## issue-story-planner との連携

1. 企画チーム L3 で **Handoff JSON** と **PlanReviewResult** を得る（planning-pm 経由）
2. スキーマ: [`../../planning/issue-story-planner/schemas/asana-buddy-handoff.v1.schema.json`](../../planning/issue-story-planner/schemas/asana-buddy-handoff.v1.schema.json)
3. 投入（review 強制例・リポジトリルートがカレント）:

```text
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\handoff_to_asana.py --handoff path\to\handoff.json --require-review-result path\to\review.json -y --if-not-exists
```

## 注意

- トークンや `.env` はリポジトリに含めない。
- 同じ `epic.title` で再実行する場合は `--if-not-exists` を使う（**sync**：親 notes 更新・不足子のみ create）。新規親を作りたい場合はタイトルを変える。
- 外部操作の前に、対話利用時はユーザー確認を前提とする（ペルソナの制約と同様）。
