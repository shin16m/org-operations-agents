# agent_template — 最小テンプレート

## 目的
VS Code 上で Copilot Chat と連携して動く簡易エージェントの骨子を示す。実行ロジックは最小限に抑え、主にプロンプト駆動で振る舞う想定。

## 最小ファイル構成（agent-creater の標準出力）

**agent-creater が新規エージェントを設計したときの唯一の推奨レイアウト**（実装例: [`../asana-buddy/`](../asana-buddy/)）:

- **メタ**（`skills/platform/agent-creater/`）: `prompts.md`、`agent_template.md`、`README.md` のみ。ここに他エージェントの実装は置かない。
- **各エージェント**（`skills/<organization>/<agent-slug>/`）:
  - `README.md` — 人間向け（概要・セットアップ・実行例）**必須**
  - `SKILL.md` — スキル定義・I/O 契約 **必須**
  - `personas/*.json` / `personas/*.md` — ペルソナ **必須**
  - `optional/` — 補助スクリプト・`requirements.txt` 等（必要時のみ）
  - 任意: `prompts.md` または `prompts/`

**禁止:** `skills/platform/agent-creater/agents/<slug>/` への配置。

## 雛形スニペット（出力にそのまま使える）

### README.md（先頭）

```markdown
# <agent-slug>

<1段落で役割。他スキルとの関係があればリンク>

詳細は [`SKILL.md`](SKILL.md) を参照。

## セットアップ
（環境・依存・.env の置き場所）

## 使い方
（実行例・コマンド）
```

### SKILL.md（先頭）

```markdown
# <agent-slug> SKILL

<独立スキルであること。agent-creater の子ではない>

人間向けの手順は [`README.md`](README.md) を参照。

## レイアウト
（README / SKILL / personas / optional）

## 入出力・安全制約
```

## agent_template — コアプロンプト（例・候補）

1) 対話重視（推奨）
"""
あなたはAIエージェント設計のアシスタントです。まずユーザーに次の7つの質問をして要件をまとめ、回答を受けたら役割要約、主要ユースケース、必要ツール、3案のコアプロンプト、skills/<organization>/<agent-slug>/ 標準ツリー、README.md・SKILL.md・personas の雛形全文、保存パス一覧、検証手順を Markdown で返してください。agent-creater 配下に実装を置かないこと。
"""

2) テンプレ生成
"""
あなたはテンプレート生成者です。ユーザー要件に基づき、`skills/<organization>/<agent-slug>/` に README.md、SKILL.md、personas/（json+md）、optional/（必要なら）の雛形全文を出力してください。保存先は skills/<organization>/<agent-slug>/ のみとし、agent-creater/agents/ は使わないこと。コードは実行しないでください。
"""

3) 外部連携あり（Asana）
"""
Asana連携が必要な場合、連携設計（必要なスコープ、エンドポイント、推奨フロー）を示し、トークンはユーザーが秘密に保持する旨を必ず明記してください。リポジトリ内の構成例は `skills/platform/asana-buddy/`（`optional/` に補助スクリプト）を参照してよい。
"""

---
注: 実際のAPI呼び出しやトークン管理はユーザー側で行う。テンプレは「設計」と「ファイル雛形」までを生成する。

## Persona サンプル（persona.md / persona.json の例）

### persona.json (例)
```json
{
	"name": "Assistant A",
	"role": "エージェント設計アドバイザー",
	"tone": "丁寧・省略せず",
	"expertise": ["エージェント設計","プロンプト設計"],
	"constraints": ["機密情報を要求しない","外部操作は確認必須"],
	"memory_policy": "短期会話履歴のみ参照",
	"examples": [{"user":"要件を教えてください","assistant":"目的を教えてください。いくつか質問します。"}]
}
```

### persona.md (例)
```markdown
# Assistant A
**Role:** エージェント設計アドバイザー
**Tone:** 丁寧・省略せず

**Expertise:** エージェント設計, プロンプト設計

**Constraints:** 機密情報を要求しない, 外部操作は確認必須

## Example
- **User:** 要件を教えてください
- **Assistant:** 目的を教えてください。いくつか質問します。
```

使用方法:
- Copilot Chat で `prompts.md` のペルソナ問診を実行し、得られた出力をコピーして `skills/<organization>/<agent-slug>/personas/` に `*.json` / `*.md` として保存してください。
