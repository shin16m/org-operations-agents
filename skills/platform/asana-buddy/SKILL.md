# asana-buddy SKILL

**独立スキル:** Asana 連携タスクアシスタント。`agent-creater` の子ではなく、`skills/platform/asana-buddy/` として `issue-story-planner` と同格に配置する。

人間向けのセットアップ・コマンド例は [`README.md`](README.md) を参照。

## 標準パイプライン

**bootstrap（L1）:**

```
workflow-orchestrator（intake）→ asana-buddy（bootstrap: 親 + 企画子 1 件）
```

**Handoff 投入（企画チーム L3・review 必須）:**

```
planning-pm → issue-story-planner → plan-reviewer（必須）→ planning-pm（gate）→ asana-buddy（本スキル）
```

- bootstrap 投入は **`--require-review-result` なし**（最小 Asana 作成）。
- 本番 Handoff 投入は **`AsanaBuddyHandoff` v1.1**（[`handoff_to_asana.py`](optional/handoff_to_asana.py)）+ **`PlanReviewResult`** + planning-pm による `handoff_approved`。
- 人間レビューのみで `plan-reviewer` を飛ばす運用は**不可**（[`workflows/planning-delivery.yaml`](../../../workflows/planning-delivery.yaml)）。
- エコシステム: [`docs/inventory/skills-inventory.md`](../../../docs/inventory/skills-inventory.md) · E2E [`docs/e2e/default-workflow.md`](../../../docs/e2e/default-workflow.md) · 基盤 Handoff 例 [`../../planning/issue-story-planner/examples/handoff.agent-workflow-orchestration.json`](../../planning/issue-story-planner/examples/handoff.agent-workflow-orchestration.json)

## レイアウト

- `README.md` — 利用者向けの概要・セットアップ・スクリプト一覧
- `SKILL.md` — このファイル（運用・ハンドオフ契約）
- `personas/` — `asana_buddy.json` / `asana_buddy.md`（Copilot 等へコピーして利用）
- `optional/` — Asana API 補助スクリプト、`requirements.txt`、`setup_venv.ps1`

エージェント専用のプロンプト束を増やす場合は、このディレクトリ直下に `prompts.md` または `prompts/` を置いてよい。

## セットアップ（Windows / PowerShell）

1. リポジトリルートで `optional/setup_venv.ps1` を実行し、ルート `.venv` に依存関係を入れる。
2. `ASANA_TOKEN` 等は **リポジトリにコミットしない**。`optional/.env`（gitignore 対象）に置くか、実行時に環境変数で渡す。

## スクリプト実行例

リポジトリルートをカレントにした場合:

```text
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\agent_handler_asana.py --project <PROJ_GID> --name "タスク名" --notes "メモ" -y
```

## 上流からの受け渡し（issue-story-planner）

課題整理・解決ストーリー・タスク案は、リポジトリの **`skills/planning/issue-story-planner/`** でスキーマ化している。Asana 投入時の単一ソースは **`AsanaBuddyHandoff` v1.1**（`schema_version`: `"1.1"`）の JSON である。

- **スキル本文**: [`../../planning/issue-story-planner/SKILL.md`](../../planning/issue-story-planner/SKILL.md)
- **JSON Schema**: [`../../planning/issue-story-planner/schemas/asana-buddy-handoff.v1.schema.json`](../../planning/issue-story-planner/schemas/asana-buddy-handoff.v1.schema.json)
- **例**: [`../../planning/issue-story-planner/examples/handoff.example.json`](../../planning/issue-story-planner/examples/handoff.example.json) · [`handoff.agent-workflow-orchestration.json`](../../planning/issue-story-planner/examples/handoff.agent-workflow-orchestration.json)

### 消費側の約束事

1. **`epic.title` / `epic.notes_markdown`** — 親タスクの `name` / `notes` に対応。一括スクリプトでは既存の `EPIC_NAME` / `EPIC_NOTES` 定数へ写経するか、小さな専用プログラムから `create_task` を呼ぶ。
2. **`subtasks`** — 配列は **着手順（先頭＝最初にやること）**。Asana が「新しいサブタスクを上に積む」表示になりやすいため、**API では配列の逆順で `create_subtask`** すること（[`optional/asana_inflation_2026_household_program.py`](optional/asana_inflation_2026_household_program.py) の `reversed(SUBTASKS)` と同じ方針）。
3. **各子タスクの Asana `notes`** — ハンドオフでは `background`（背景）・`summary`（概要）・`done_when`（完了条件）が**必須**。消費側はこれらを 1 本の `notes` にまとめる（例: `## 背景` / `## 概要` / `## 完了条件` の Markdown 見出しで連結）。`pillar` がある場合は先頭に `柱: {pillar}\n\n` を付けてから続けてよい。

単発タスクのみなら引き続き `agent_handler_asana.py` の `--name` / `--notes` を使う。

親＋子の一括は次のいずれか:

- **推奨:** [`optional/handoff_to_asana.py`](optional/handoff_to_asana.py) — 新規作成、または `--if-not-exists` / `--parent` で**既存親へ sync**（bootstrap 後の本番 Handoff 投入）
- **補助:** [`optional/sync_handoff_epic.py`](optional/sync_handoff_epic.py) — 同上 sync + `--complete-through N --complete-only` で一括完了
- **テーマ別:** `asana_<テーマ>_program.py` — 定数 `SUBTASKS` から投入（[`asana_program_common.py`](optional/asana_program_common.py) の `notes_from_legacy_body` で v1.1 形式に整形）

## 一括プログラムの命名

テーマ別の親タスク＋サブタスク投入用は `optional/asana_<テーマ>_program.py`（例: 物価・家計、社会課題、`optional/asana_hikikomori_support_program.py`（ひきこもり支援）、`optional/asana_ai_agent_adoption_program.py`（AIエージェント普及の阻害要因））を置く。

## task-executor 連携（読取・完了）

| スクリプト | 用途 |
|------------|------|
| [`optional/fetch_task.py`](optional/fetch_task.py) | `--gid` で name / notes / completed を表示。`--list-subtasks` で子一覧 |
| [`optional/comment_task.py`](optional/comment_task.py) | 署名付きコメント（`--agent` / `--skill` / `--body` または `--from-json`） |
| [`optional/complete_task.py`](optional/complete_task.py) | `--gid -y` で完了マーク（**comment の後**） |
| [`optional/sync_handoff_epic.py`](optional/sync_handoff_epic.py) | `--complete-through N --complete-only` で子【1/N】…【N/N】を一括完了 |

**運用:** ローカルで `done_when` を満たしたら、**必ず** `comment_task.py` で署名コメント → `complete_task.py` で完了（product-manager / 各実行スキル）。詳細は [`docs/design/agent-asana-comment-signature.md`](../../../docs/design/agent-asana-comment-signature.md) · [`docs/design/dept-work-io.md`](../../../docs/design/dept-work-io.md)。

実行本体は [`task-executor`](../task-executor/SKILL.md)。本スキルは Asana API の薄いラッパのみ。

## 環境変数

Asana 用 `.env` の標準置き場所は **`optional/.env`（本スキル直下）** です。
