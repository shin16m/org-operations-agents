# agent-creater SKILL

## 概要
`agent-creater` は、AIエージェント（主にVS Code上でCopilot/Chatと連携して動作するエージェント）の設計と最小実装テンプレを生成・提案するための **メタスキル** です。対話を通じて要件を問診し、柔軟で運用しやすいエージェント設計書とプロンプト候補、最小ファイル構成を返します。

このリポジトリでは **作成した各エージェントを `skills/agent-creater/agents/<agent-slug>/` にまとめる** 方針です（ペルソナ・オプションスクリプト・エージェント固有ドキュメントを同居）。例: [`agents/asana-buddy/AGENT.md`](agents/asana-buddy/AGENT.md)

関連: 課題整理から Asana 用ハンドオフ JSON までを出す **`skills/issue-story-planner/SKILL.md`**（[`issue-story-planner`](../issue-story-planner/SKILL.md)）を upstream とし、実タスク作成は `asana-buddy` に渡す二段構成にできる。

## フォルダ契約（1 エージェント = 1 スラッグ）

ルート: `skills/agent-creater/agents/<agent-slug>/`

| 要素 | 内容 |
|------|------|
| **スラッグ** | `kebab-case`、ASCII のみ（例: `asana-buddy`, `invoice-helper`）。表示名はペルソナや AGENT 本文で別途定義。 |
| **AGENT.md** | そのエージェント束の入口（役割概要・レイアウト・運用・スクリプト実行例）。Cursor のトップレベル `SKILL.md` と混同しないため **エージェント単位は AGENT.md** を既定とする。 |
| **personas/** | `*.json` / `*.md` のペルソナ定義（必要なら複数）。 |
| **optional/** | 外部 API 連携スクリプト、`requirements.txt`、セットアップ用 `setup_venv.ps1` など。機密はコミットしない（`.env` は gitignore）。 |
| **prompts.md** または **prompts/** | エージェント専用の問診・コアプロンプトだけを分けたい場合に追加。共通テンプレはこのメタスキル直下の [`prompts.md`](prompts.md) を参照してよい。 |

メタスキル直下（`skills/agent-creater/`）には、全エージェント共通の [`prompts.md`](prompts.md)、[`agent_template.md`](agent_template.md)、[`README.md`](README.md) を置く。

### 新規エージェント作成チェリスト

1. `agents/<agent-slug>/` を作成し、`AGENT.md` を書く（目的・入出力・注意事項・スクリプトの実行方法）。
2. `personas/` に JSON/Markdown を置く（または `prompts.md` のペルソナ問診の出力をここへ保存する手順を AGENT.md に書く）。
3. 外部連携が必要なら `optional/` にスクリプトと `requirements.txt` を置く。API キーはリポジトリに含めない。
4. エージェント固有プロンプトがメタと分離したいなら `prompts.md` または `prompts/` を追加。
5. メタの [`agent_template.md`](agent_template.md) の「最小ファイル構成」を必要に応じて更新する提案をレビューに含める。

### レガシー配置について

以前は `personas/*.json` と `optional/*` を `skills/agent-creater/` 直下に置いていた。新規作業は **`agents/<slug>/` 配下に統一**する。既存のブックマークやローカル `.env` を古い `optional/` に置いていた場合は、対応する `agents/<slug>/optional/` へ移す。

## 能力
- ユーザー問診テンプレを提示し要件を整理する
- エージェントの役割定義、インプット/アウトプット設計を生成する
- Copilot Chat で使えるプロンプトテンプレ（複数候補）を生成する
- 上記フォルダ契約に沿った最小ファイル構成（AGENT.md / personas / optional）を提案する
- 外部連携（例: Asana）の設計アドバイス（実鍵はユーザーが管理）

## 入力（想定）
- 目的（自動化したい業務やゴール）
- 想定ユーザー（開発者/PM/非技術者）
- 実行環境の希望（例: Python / VS Code）
- 必要な外部ツール（Asana等）と利用方法（オプション）
- 柔軟性の度合い（対話重視／ワークフロー重視）

## 出力（想定）
1. 役割記述（1段落）
2. 要件問診テンプレ（質問リスト）
3. コアプロンプト（3案）
4. `agents/<agent-slug>/` を根とした最小ファイル構成案（各ファイルの役割の一言）
5. テスト/検証手順（簡易）

## 安全制約と運用上の注意
- **Asana サブタスクを一括作成する場合:** 画面上で「リスト先頭＝最初に手を付ける仕事」にしたいワークフローでは、Asana が新規サブタスクを上に積む表示になりがちなので、**意図した順序の逆から API で作成する**（例: `reversed(SUBTASKS)`）。表示順が環境で異なる場合は実際の並びを一度確認してから順序を決める。
- 外部APIキー（Asana等）はユーザーが明示的に提供する場合のみ扱う。スキル自体はキーを保存しない。
- 自動で外部コマンドを実行するテンプレは提供しない。ユーザー実行を前提とする。
- 機密データはプロンプトに含めないよう注意喚起する。

## 利用方法（Copilot Chat内での利用例）
1. Copilot Chat にてこのSKILLの役割を短く伝える（例: 「あなたはagent-createrスキルです。以下の要件を元にエージェント設計を出してください」）
2. `prompts.md` の「初期問診」を実行してユーザーから情報を収集する
3. 生成された設計を確認し、必要なら対話で微調整する

## 例（簡略）
- 入力要件: "小規模チーム向けにAsanaと連携するタスク作成アシスタント。VS Code内で対話中心。"
- 出力: 役割定義、3つのコアプロンプト、`agents/asana-buddy/` 型の最小構成案（AGENT.md, personas, optional）

---
このSKILLは「設計支援」と「テンプレ生成」に特化しています。実際のLLM呼び出しやAPI連携はユーザー側で管理してください。

## アクション: Generate Persona
目的: ユーザーと対話してペルソナ定義を作成し、`persona.json`（機械用）と`persona.md`（人間用）としてコピー保存できる出力を生成します。自動ファイル書き込みは行いません。

実行フロー:
1. `prompts.md` の「ペルソナ問診」を実行し、ユーザーから必要情報を収集する。
2. 収集した回答を基に、LLMに対して「1) JSONブロック 2) Markdown（persona.md）」の順で出力するよう指示する。
3. 出力をユーザーに表示し、保存先として **`agents/<agent-slug>/personas/`**（スラッグが未定なら仮名でよい）を案内する。

安全ルール:
- 自動で外部APIやコマンドを実行しないこと。
- APIトークンや機密情報はプロンプトに含めさせないか、明示的な同意がある場合のみユーザー側で提供する。
- 出力ファイルを保存する際はユーザーに操作を委ねる（コピー&保存を案内）。

利用例（Copilot Chat内）:
"""
あなたはagent-createrスキルです。ペルソナ生成を開始してください。まずペルソナ名、役割、トーン、専門、制約、記憶ポリシー、例の順で質問してください。
"""
