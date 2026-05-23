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

   `ASANA_PROJECT_ID` が無い場合、一部の一括スクリプトはテスト用プロジェクト GID にフォールバックします（stderr に注意が出ます）。

3. プロジェクト GID の確認:

   ```powershell
   .\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\asana_inflation_2026_household_program.py --list-projects
   ```

   （他の `asana_*_program.py` でも `--list-projects` は利用可能です。）

## スクリプト一覧

| スクリプト | 用途 |
|------------|------|
| `agent_handler_asana.py` | 単発タスク作成（`-y` で確認スキップ） |
| `handoff_to_asana.py` | **Handoff JSON v1.1** から親＋子を一括作成（推奨） |
| `fetch_task.py` | タスク読取（`task-executor` 用） |
| `comment_task.py` | **署名付き**エージェント作業コメント（[`agent-asana-comment-signature.md`](../../../docs/design/agent-asana-comment-signature.md)） |
| `complete_task.py` | タスク完了マーク（**comment の後**） |
| `asana_delete_task.py` | タスク削除（`-y` 必須） |
| `asana_program_common.py` | 共有: notes 組み立て・プロジェクト解決・逆順作成 |
| `asana_<テーマ>_program.py` | テーマ別の親＋子一括（`--if-not-exists` / `--dry-run` 対応） |

同梱のテーマ別プログラム例:

- `asana_japan_social_issues_program.py` — 日本の社会課題
- `asana_inflation_2026_household_program.py` — 物価・家計
- `asana_hikikomori_support_program.py` — ひきこもり支援
- `asana_ai_agent_adoption_program.py` — AI エージェント普及の阻害要因

## 実行例

**単発タスク**（リポジトリルートがカレント）:

```text
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\agent_handler_asana.py --project <PROJ_GID> --name "タスク名" --notes "メモ" -y
```

**一括（重複作成を避ける）**:

```text
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\asana_hikikomori_support_program.py -y --if-not-exists
```

サブタスクは一覧で **上から順に消化** しやすいよう、API では定義リストの **逆順** で作成します（[`SKILL.md`](SKILL.md) 参照）。

## 標準パイプライン（workflow v2）

1. [`workflow-orchestrator`](../workflow-orchestrator/README.md)（**intake**）— 課題を渡す
2. [`issue-story-planner`](../../planning/issue-story-planner/SKILL.md) — Handoff JSON
3. [`plan-reviewer`](../../planning/plan-reviewer/SKILL.md) — **必須** `PlanReviewResult`
4. [`workflow-orchestrator`](../workflow-orchestrator/SKILL.md)（**gate**）— execute 可否
5. 本スキル — Asana 投入

詳細: [`docs/e2e/default-workflow.md`](../../../docs/e2e/default-workflow.md)

## issue-story-planner との連携

1. 上記パイプラインで **Handoff JSON** と **PlanReviewResult** を得る
2. スキーマ: [`../../planning/issue-story-planner/schemas/asana-buddy-handoff.v1.schema.json`](../../planning/issue-story-planner/schemas/asana-buddy-handoff.v1.schema.json)
3. 投入（review 強制例・リポジトリルートがカレント）:

```text
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\handoff_to_asana.py --handoff path\to\handoff.json --require-review-result path\to\review.json -y --if-not-exists
```

## 注意

- トークンや `.env` はリポジトリに含めない。
- 同じエピック名で `-y` のみ再実行するとタスクが重複する。再実行時は `--if-not-exists` を使う。
- 外部操作の前に、対話利用時はユーザー確認を前提とする（ペルソナの制約と同様）。
