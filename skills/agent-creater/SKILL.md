# agent-creater SKILL

## 概要
`agent-creater` は、AIエージェント（主にVS Code上でCopilot/Chatと連携して動作するエージェント）の設計と最小実装テンプレを生成・提案するための **メタスキル** です。対話を通じて要件を問診し、柔軟で運用しやすいエージェント設計書とプロンプト候補、最小ファイル構成を返します。

**本スキルは特定エージェントの実装を含みません。** リポジトリ内の実装済みスキル例: [`../asana-buddy/SKILL.md`](../asana-buddy/SKILL.md)（Asana タスク化）、[`../issue-story-planner/SKILL.md`](../issue-story-planner/SKILL.md)（課題→ストーリー→ハンドオフ JSON）。後者と asana-buddy は **上流→下流** の組み合わせ例（設計は issue-story-planner、Asana 作成は asana-buddy）。

## 新規エージェント作成の唯一の入口（リポジトリ運用）

本リポジトリで **`skills/<slug>/` を新規に作るときは本スキル（agent-creater）にのみ委任**する。`issue-story-planner`・`plan-reviewer`・`workflow-orchestrator` は他スキルの雛形を書かない。

生成後: [`workflows/agent-registry.yaml`](../../workflows/agent-registry.yaml) 登録 → [`workflows/default.yaml`](../../workflows/default.yaml) 等を更新（[`CONTRIBUTING.md`](../../CONTRIBUTING.md)）。

## エコシステム（本リポジトリ）

```
agent-creater（新規スキル生成のみ）
    ↓ 登録
workflows/agent-registry.yaml + workflows/*.yaml
    ↓ 段階実行
workflow-orchestrator（intake）→ issue-story-planner → plan-reviewer（必須）→ workflow-orchestrator（gate）→ asana-buddy
```

参照: [`docs/inventory/skills-inventory.md`](../../docs/inventory/skills-inventory.md) · 設計 Handoff [`../issue-story-planner/examples/handoff.agent-workflow-orchestration.json`](../issue-story-planner/examples/handoff.agent-workflow-orchestration.json)

## フォルダ契約（1 エージェント = 1 スラッグ）

ルート: **`skills/<agent-slug>/`**（`agent-creater` の子ディレクトリではない）

| 要素 | 内容 |
|------|------|
| **スラッグ** | `kebab-case`、ASCII のみ（例: `asana-buddy`, `invoice-helper`）。表示名はペルソナや SKILL 本文で別途定義。 |
| **README.md** | 人間向けの概要・セットアップ・実行例（**必須**）。 |
| **SKILL.md** | Cursor / Copilot 向けのスキル定義・運用・I/O 契約（**必須**）。 |
| **personas/** | `*.json` / `*.md` のペルソナ定義（**必須**）。 |
| **optional/** | 外部 API 連携スクリプト、`requirements.txt` 等（必要時のみ）。機密はコミットしない（`.env` は gitignore）。 |
| **prompts.md** または **prompts/** | エージェント専用の問診・コアプロンプトだけを分けたい場合に追加。 |

メタスキル直下（`skills/agent-creater/`）には、全エージェント共通の [`prompts.md`](prompts.md)、[`agent_template.md`](agent_template.md)、[`README.md`](README.md) のみを置く（**`agents/` や `optional/` は置かない**）。

### 標準出力ツリー（agent-creater が生成する成果物）

新規エージェントを設計したら、**必ず次のツリーで出力・保存先を案内する**（参照実装: [`../asana-buddy/`](../asana-buddy/)）。

```text
skills/
└── <agent-slug>/
    ├── README.md          # 人間向け（必須）
    ├── SKILL.md           # スキル定義（必須）
    ├── personas/
    │   ├── <persona-name>.json
    │   └── <persona-name>.md
    ├── optional/          # 外部連携・スクリプトがある場合のみ
    │   ├── requirements.txt
    │   └── ...
    └── prompts.md         # 任意
```

**禁止:** `skills/agent-creater/agents/<slug>/` や `agent-creater` 配下への実装配置を提案しない（レガシー）。

**出力時に含めること:** 上記ツリー、各ファイルの**全文または雛形**（ユーザーがコピー保存できる形）、保存パス一覧、検証手順。

### 新規エージェント作成チェックリスト

1. スラッグを決め、`skills/<agent-slug>/` を新規作成する（**`agent-creater` の外**）。
2. **`README.md`**（セットアップ・実行例）と **`SKILL.md`**（スキル契約）を書く。README から SKILL へリンクする。
3. **`personas/`** に JSON と Markdown を置く（ペルソナ問診の出力をここへ保存する手順を README に書く）。
4. 外部連携が必要なら **`optional/`** にスクリプトと `requirements.txt` を置く。API キーはリポジトリに含めない。
5. 必要なら `prompts.md` を追加。他スキルとの連携（例: issue-story-planner → asana-buddy）があれば SKILL.md に I/O を明記する。

## 能力
- ユーザー問診テンプレを提示し要件を整理する
- エージェントの役割定義、インプット/アウトプット設計を生成する
- Copilot Chat で使えるプロンプトテンプレ（複数候補）を生成する
- 上記フォルダ契約に沿った最小ファイル構成（README.md / SKILL.md / personas / optional）を提案する
- 外部連携（例: Asana）の設計アドバイス（実鍵はユーザーが管理）

## 入力（想定）
- 目的（自動化したい業務やゴール）
- 想定ユーザー（開発者/PM/非技術者）
- 実行環境の希望（例: Python / VS Code）
- 必要な外部ツール（Asana等）と利用方法（オプション）
- 柔軟性の度合い（対話重視／ワークフロー重視）

## 出力（想定）

設計完了時は、次を **このリポジトリの標準レイアウト**（`skills/<agent-slug>/`）で返す:

1. 役割記述（1段落）
2. 要件問診テンプレ（質問リスト）— 既に実施済みなら省略可
3. コアプロンプト（3案）
4. **標準出力ツリー**（上記）と、**README.md / SKILL.md / personas の雛形全文**（コピー保存可能なコードブロック）
5. `optional/` が必要な場合はファイル一覧と各ファイルの雛形
6. 保存パス一覧（例: `skills/my-agent/README.md`）
7. テスト/検証手順（3ステップ以内）

## 安全制約と運用上の注意
- **Asana サブタスクを一括作成する場合:** 画面上で「リスト先頭＝最初に手を付ける仕事」にしたいワークフローでは、Asana が新規サブタスクを上に積む表示になりがちなので、**意図した順序の逆から API で作成する**（例: `reversed(SUBTASKS)`）。表示順が環境で異なる場合は実際の並びを一度確認してから順序を決める。実装例は [`../asana-buddy/`](../asana-buddy/SKILL.md)。
- 外部APIキー（Asana等）はユーザーが明示的に提供する場合のみ扱う。スキル自体はキーを保存しない。
- 自動で外部コマンドを実行するテンプレは提供しない。ユーザー実行を前提とする。
- 機密データはプロンプトに含めないよう注意喚起する。

## 利用方法（Copilot Chat内での利用例）
1. Copilot Chat にてこのSKILLの役割を短く伝える（例: 「あなたはagent-createrスキルです。以下の要件を元にエージェント設計を出してください」）
2. `prompts.md` の「初期問診」を実行してユーザーから情報を収集する
3. 生成された設計を確認し、必要なら対話で微調整する

## 例（簡略）
- 入力要件: "小規模チーム向けにAsanaと連携するタスク作成アシスタント。VS Code内で対話中心。"
- 出力: 役割定義、3つのコアプロンプト、`skills/<new-slug>/` 標準ツリーと README.md・SKILL.md・personas の雛形全文。参照例: [`../asana-buddy/`](../asana-buddy/README.md)。

---
このSKILLは「設計支援」と「テンプレ生成」に特化しています。実際のLLM呼び出しやAPI連携はユーザー側で管理してください。

## アクション: Generate Persona
目的: ユーザーと対話してペルソナ定義を作成し、`persona.json`（機械用）と`persona.md`（人間用）としてコピー保存できる出力を生成します。自動ファイル書き込みは行いません。

実行フロー:
1. `prompts.md` の「ペルソナ問診」を実行し、ユーザーから必要情報を収集する。
2. 収集した回答を基に、LLMに対して「1) JSONブロック 2) Markdown（persona.md）」の順で出力するよう指示する。
3. 出力をユーザーに表示し、保存先として **`skills/<agent-slug>/personas/`**（スラッグが未定なら仮名でよい）を案内する。

安全ルール:
- 自動で外部APIやコマンドを実行しないこと。
- APIトークンや機密情報はプロンプトに含めさせないか、明示的な同意がある場合のみユーザー側で提供する。
- 出力ファイルを保存する際はユーザーに操作を委ねる（コピー&保存を案内）。

利用例（Copilot Chat内）:
"""
あなたはagent-createrスキルです。ペルソナ生成を開始してください。まずペルソナ名、役割、トーン、専門、制約、記憶ポリシー、例の順で質問してください。
"""
