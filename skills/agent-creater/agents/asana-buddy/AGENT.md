# Asana Buddy（エージェント束）

このフォルダは **1 エージェント = 1 ディレクトリ** 方針のリポジトリ内例です。Asana 連携タスクアシスタント用のペルソナとオプションスクリプトをまとめています。

## レイアウト

- `AGENT.md` — このファイル（人間向けの入口・運用メモ）
- `personas/` — `asana_buddy.json` / `asana_buddy.md`（Copilot 等へコピーして利用）
- `optional/` — Asana API 補助スクリプト、`requirements.txt`、`setup_venv.ps1`

共通の問診・テンプレはメタスキル側の `skills/agent-creater/prompts.md` および `agent_template.md` を参照してください。エージェント専用のプロンプト束を増やす場合は、このディレクトリ直下に `prompts.md` または `prompts/` を置いてよいです。

## セットアップ（Windows / PowerShell）

1. リポジトリルートで `optional/setup_venv.ps1` を実行し、ルート `.venv` に依存関係を入れる。
2. `ASANA_TOKEN` 等は **リポジトリにコミットしない**。`optional/.env`（gitignore 対象）に置くか、実行時に環境変数で渡す。

## スクリプト実行例

リポジトリルートをカレントにした場合:

```text
.\.venv\Scripts\python.exe .\skills\agent-creater\agents\asana-buddy\optional\agent_handler_asana.py --project <PROJ_GID> --name "タスク名" --notes "メモ" -y
```

## 一括プログラムの命名

テーマ別の親タスク＋サブタスク投入用は `optional/asana_<テーマ>_program.py`（例: 物価・家計、社会課題、`optional/asana_hikikomori_support_program.py`（ひきこもり支援））を置く。

## 移行メモ

以前は `skills/agent-creater/personas/asana_buddy.*` と `skills/agent-creater/optional/*` に分かれていました。参照は本パスに統一してください。Asana 用の `.env` の標準置き場所は **`optional/.env`（本フォルダ直下）** です。旧 `skills/agent-creater/optional/.env` にだけファイルがある場合も、スクリプトがフォールバック読み込みします。
