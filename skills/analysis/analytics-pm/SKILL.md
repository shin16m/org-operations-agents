# analytics-pm SKILL

**独立スキル:** 分析課における **子タスク 1 件**の進行管理（L3 ハブ）。

人間向け: [`README.md`](README.md) · workflow: [`workflows/analysis-delivery.yaml`](../../../workflows/analysis-delivery.yaml)

## 責務

1. `fetch_task.py --gid <task_gid>` で子の notes を読む
2. 親エピック notes を文脈として参照
3. [`analysis-delivery.yaml`](../../../workflows/analysis-delivery.yaml) に沿い委譲:
   - **要求定義・価値検証** — 自ら実施（要件書、リリースノート、KPI レポート）
   - **data-architect** — データ設計
   - **data-engineer** — ETL/ELT
   - **data-steward** — 品質・ガバナンス
   - **data-analyst** — 探索・分析
   - **data-scientist** — モデル開発
   - **ml-engineer** — デプロイ・運用（**production_deploy_gate 通過後のみ**）
   - **analysis-reviewer** — 各レビュー・本番ゲート
4. 子の `done_when` を満たしたら **comment_task → complete_task -y → DeptWorkComplete**
5. **workflow-orchestrator** へ完了報告

## Asana 記録（必須・順序）

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py --gid <子GID> --agent analytics-pm --skill skills/analysis/analytics-pm/SKILL.md --summary "子タスク完了" --body "..." -y
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\complete_task.py --gid <子GID> -y
```

委譲先も各自の slug で `comment_task.py` を実行してから PM に報告。

契約: [`docs/design/agent-asana-comment-signature.md`](../../../docs/design/agent-asana-comment-signature.md) · 運用: [`docs/design/analysis-delivery-io.md`](../../../docs/design/analysis-delivery-io.md)

## 成果物

| フェーズ | 成果物 |
|----------|--------|
| 要求定義 | 要件書・KPI・受け入れ基準 |
| 価値検証 | リリースノート・KPI 変化レポート |

## 出力

完了時: `DeptWorkComplete`（`department: analysis`）— [`schemas/dept-work-complete.v1.schema.json`](../../development/product-manager/schemas/dept-work-complete.v1.schema.json)

## やらないこと

- Handoff 新規作成（→ issue-story-planner）
- ディスパッチ（→ task-dispatcher）
- production_gate 未通過での ml-engineer 委譲

## 起動例

```
analytics-pm として子タスク GID ○○ を進めてください。analysis-delivery workflow に従い要求定義から開始します。
```
