# analytics-pm SKILL

**独立スキル:** 分析チームにおける **子タスク 1 件**の進行管理（L3 ハブ）。

人間向け: [`README.md`](README.md) · workflow: [`workflows/analysis-delivery.yaml`](../../../workflows/analysis-delivery.yaml) · **厳密アサイン:** [`docs/design/analytics-pm-assignment.md`](../../../docs/design/analytics-pm-assignment.md) · **dispatch 起動:** [`docs/design/dispatch-prompt-ssot.md`](../../../docs/design/dispatch-prompt-ssot.md#analysis)

## 厳密運用（必須）

1. **自分で実装しない**（要求定義・進行・親タスク完了集約を除く）。
2. 子タスクを分析し、**担当エージェント**を決める → **Asana サブタスク**を作成し各 notes に `担当: <slug>` を書く（`pm_assign_subtasks.py` 必須。親 `担当:` 書き換えのみ禁止）。
3. 担当エージェントが `fetch_task.py --show-assignee` で自分の slug と一致することを確認してから実行。
4. 委譲先が **comment_task** → PM が子サブタスクを **complete** → 全サブ完了後に親を **comment → complete**。

```powershell
# チーム内サブタスク作成（プラン JSON）
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent <親GID> --plan .\work\assign-plans\fishing-task-1-strict.json -y

# 担当追記のみ
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\update_task_notes.py `
  --gid <GID> --assignee data-engineer --preserve-body -y
```

再実施時: 完了タスクは `complete_task.py --undo -y`。成果物は `output/analysis/strict-v2/`（旧 bulk は `_archive/` 参照のみ）。

## 責務

1. `fetch_task.py --gid <task_gid> --show-assignee` で子の notes を読む
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

- Handoff 新規作成（→ 企画チーム）
- Handoff JSON をチーム間入力として読む（→ Asana 子 notes を読む）
- ディスパッチ（→ task-dispatcher）
- production_gate 未通過での ml-engineer 委譲

## 起動例

```
analytics-pm として子タスク GID ○○ を進めてください。analysis-delivery workflow に従い要求定義から開始します。
```
