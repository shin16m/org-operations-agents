# issue-story-planner（課題整理 → 解決ストーリー → タスク案）

## 概要

このスキルは、**課題点の整理**、**解決ストーリー（なぜその順序で進めるか）**、**Asana 等に落とし込める粒度のタスク案**までを一気通貫でまとめる。外部 API は呼ばず、**構造化アウトプット**を返す。実際の Asana 作成は [`asana-buddy`](../asana-buddy/SKILL.md) スキル（スクリプト／対話）に委ねる。

## 推奨パイプライン（plan スロット）

```
issue-story-planner（本スキル）→ plan-reviewer → workflow-orchestrator → asana-buddy
```

- **新規エージェント**をタスク案に含める場合、実装は [`agent-creater`](../agent-creater/SKILL.md) に委任と明記する（本スキルは `skills/<slug>/` を生成しない）。
- `plan-reviewer` 未使用時は人間が Handoff をレビューしてから Asana 投入してよい。
- registry / workflow の詳細は [`docs/design/workflow-io-contract.md`](../../docs/design/workflow-io-contract.md)（本格な SKILL 相互リンクは今後整備）。

## いつ使うか

- テーマやプロジェクトの「課題」「前提」「ゴール」がまだ文章に散らばっている
- 対策のストーリーライン（誰が・何を・どの順で）を言語化したい
- そのままタスク管理ツールへ渡せる単位まで分解したい（**提案**まで。作成は別手順）

## 実行フロー（モデル向け）

1. **スコープ確認** — 対象（個人／チーム／プロダクト）、期限の有無、禁止事項（例: 投資助言をしない）。
2. **課題の棚卸し** — 事実と解釈を分け、曖昧さは「要確認」として明示。
3. **解決ストーリー** — 因果と優先順位（短期止血 → 構造対応 等）を 1 本のナラティブにまとめる。
4. **タスク案** — 親エピック 1 件＋子タスク複数。各子は **着手順が分かる `title`** に加え、**必ず** 次の 3 フィールドを埋める（いずれも空文字不可）:
   - **`background`（背景）** — なぜこの仕事があるか、前提・制約・文脈。
   - **`summary`（概要）** — 何をするかを平易に。
   - **`done_when`（完了条件）** — 完了とみなす具体的な条件・受け入れ基準。
5. **ハンドオフ** — 次節の **I/O 契約** に従い、`AsanaBuddyHandoff` JSON（**スキーマ v1.1**）を必ず出力する。人間向けの要約 Markdown を続けてよい。

## 安全・品質ルール

- 機密・個人識別情報を要求しない。推測は「推測」とラベルする。
- 医療・法律・投資など専門領域は**一般情報の整理**に留め、助言と断定を避ける。
- 外部コマンドや API の実行はこのスキルでは行わない（ユーザー実行）。

---

## I/O 契約（Asana Buddy 連携）

### 設計原則

- **単一の真実源**: 機械可読は **JSON 1 ブロック**（スキーマ [`schemas/asana-buddy-handoff.v1.schema.json`](schemas/asana-buddy-handoff.v1.schema.json)）。同じ内容の繰り返しを Markdown で冗長に書かない。
- **サブタスクの順序**: `subtasks[]` は **画面上で上から「最初に着手する仕事」が先頭**になる並び（＝ユーザーがリスト上から順に消化する想定）。Asana API では新規サブタスクが上に積まれる挙動がありやすいため、**実装側は配列の逆順で作成する**（`asana-buddy` の既存プログラムと同じ方針）。JSON では **常に「正しい着手順」** で並べる。
- **親タスクの `notes`**: `epic.notes_markdown` に **課題整理・解決ストーリー・進め方** をまとめた 1 本の Markdown を入れる（Asana の task `notes` にそのまま載せられる想定）。親エピックに `background` / `summary` / `done_when` の並列フィールドは**不要**（ナラティブでよい）。**必須なのは各 `subtasks[]` 要素の 3 フィールド**。
- **子タスクの Asana `notes`**: スキーマ上は `background` / `summary` / `done_when` に分割して保持する。**消費側**は Asana の `notes` 用に、例として次のような Markdown 見出しで連結する（ラベルは日本語でも英語でもよいが、意味は固定）:

```markdown
## 背景
{background の本文}

## 概要
{summary の本文}

## 完了条件
{done_when の本文}
```

  `pillar` がある場合は先頭に `柱: …` 行を付けてから上記ブロックを続けてもよい。

### `AsanaBuddyHandoff` v1.1（フィールド説明）

| フィールド | 必須 | 説明 |
|------------|------|------|
| `schema_version` | はい | **`"1.1"`** 固定（v1.0 からの破壊的変更: 子タスクの必須フィールド追加）。 |
| `meta.title` | いいえ | 人間用のバンドル名（チャット見出し用）。 |
| `meta.locale` | いいえ | 例: `"ja-JP"`。 |
| `epic.title` | はい | Asana 親タスク名（短く一意に）。 |
| `epic.notes_markdown` | はい | 課題整理・ストーリー・運用メモを含む Markdown。 |
| `subtasks` | はい | 子タスクの配列（着手順＝先頭から）。 |
| `subtasks[].title` | はい | Asana 子タスク名。 |
| `subtasks[].background` | はい | **背景** — 文脈・前提・なぜこのタスクか（`minLength` 1）。 |
| `subtasks[].summary` | はい | **概要** — 何をするか（`minLength` 1）。 |
| `subtasks[].done_when` | はい | **完了条件** — 完了の定義・受け入れ基準（`minLength` 1）。 |
| `subtasks[].pillar` | いいえ | 列・スイムレーン名。スクリプトでは `柱: {pillar}` 行を先頭に付与してよい。 |

**モデル向け必須ルール:** `subtasks` の**各要素**について `title`・`background`・`summary`・`done_when` をすべて非空で埋める。省略・プレースホルダのみは不可。

### 消費側（asana-buddy）の責務

1. JSON を検証（スキーマに対する相対パスは本スキルフォルダの `schemas/`）。
2. `epic` → `agent_handler_asana.py` の `--name` / `--notes`、または一括プログラム内の定数へ写経（または小さなジェネレータスクリプトをユーザーが実行）。
3. `subtasks` → `create_subtask` を **`subtasks` 配列の逆順** で呼ぶ。各子の `notes` 引数は **`background` / `summary` / `done_when`** を所定の見出し付き Markdown 等に連結して組み立てる。

### 利用例（Copilot / Cursor 内）

```
あなたは issue-story-planner スキルです。テーマ「〈ここに題材〉」について課題整理・解決ストーリー・タスク案を出し、
最後に AsanaBuddyHandoff 準拠（schema_version "1.1"、各 subtask に background・summary・done_when 必須）の JSON コードブロックを1つだけ出力してください。
```

---

## 出力テンプレート（モデルはこの順でよい）

1. 箇条書きサマリ（任意・短く）
2. ` ```json ` で囲んだ **単一** の `AsanaBuddyHandoff` オブジェクト
3. （任意）ユーザーがコピーしやすい Asana 用の一行メモ

このスキルは **設計・文書化** に特化する。Asana トークンやプロジェクト GID は [`asana-buddy`](../asana-buddy/SKILL.md) 側の運用に従う。

## エコシステム・例

| リソース | 用途 |
|----------|------|
| [`examples/handoff.example.json`](examples/handoff.example.json) | 汎用 Handoff 例 |
| [`examples/handoff.agent-workflow-orchestration.json`](examples/handoff.agent-workflow-orchestration.json) | 基盤エピック・メタ設計の参照 Handoff |
| [`docs/design/workflow-io-contract.md`](../../docs/design/workflow-io-contract.md) | パイプライン I/O |
| [`workflows/default.yaml`](../../workflows/default.yaml) | 宣言的 workflow |

**本スキルは新規 `skills/<slug>/` を生成しない** → [`agent-creater`](../agent-creater/SKILL.md)。
