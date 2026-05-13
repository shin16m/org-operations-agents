Asana 用スクリプトは `agents/asana-buddy/optional/` にあります。

ローカルの Asana 用 `.env`（`ASANA_TOKEN` など）も **`agents/asana-buddy/optional/.env`** に置いてください（gitignore 済み）。リポジトリルートの `.env` を使う運用でも構いません（探索順は「カレントから上」「スクリプト所在から上」のいずれかで最初に見つかったファイルが使われます）。

旧パス `skills/agent-creater/optional/.env` にファイルが残っている場合も、`agent_handler_asana.py` の探索で読み込まれます（後方互換用）。
