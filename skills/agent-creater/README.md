# agent-creater スキル利用 README

**メタスキル:** 新しいエージェントの設計と雛形を出す。作ったエージェントの実体は **`skills/<agent-slug>/`** に置く（`agent-creater` の中には置かない）。完成例: [`../asana-buddy/`](../asana-buddy/)。

## 使い方（概要）

1. VS Code の Copilot Chat で、`skills/agent-creater/prompts.md` にある「初期問診テンプレ」を貼り付けて実行してください。
2. ユーザーの回答を集めたら、`prompts.md` の「出力フォーマット指示」に従い、**`skills/<agent-slug>/` 標準ツリー**と **README.md / SKILL.md / personas の雛形全文**を生成します。
3. 生成された結果をレビューし、ユーザーが示されたパスにコピー保存します。

## 標準出力（必ずこの形）

```text
skills/<agent-slug>/
├── README.md
├── SKILL.md
├── personas/
│   ├── *.json
│   └── *.md
└── optional/     # 必要時のみ
```

詳細契約は [`SKILL.md`](SKILL.md) と [`agent_template.md`](agent_template.md) を参照。

## 注意点

- 外部 API キー（Asana 等）はこのリポジトリに含めず、各スキルの `optional/.env` 等でユーザーが管理する。
- **`skills/agent-creater/agents/` への配置はしない**（廃止済み）。
