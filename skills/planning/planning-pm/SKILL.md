# planning-pm SKILL

**独立スキル:** 企画チームにおける **子タスク 1 件**の進行管理（L3 ハブ）。

人間向け: [`README.md`](README.md) · workflow: [`workflows/planning-delivery.yaml`](../../../workflows/planning-delivery.yaml) · I/O: [`docs/design/planning-delivery-io.md`](../../../docs/design/planning-delivery-io.md)

## ミッション

**企画チームの成果（Handoff + PlanReviewResult）を Asana タスク群に落とし込む。** 実行系子タスク（development / analysis）は `handoff_to_asana.py` 投入後、オーケストレーターが task-dispatcher で各チームへ配賦する。

## 責務

1. `fetch_task.py --gid <task_gid>` で企画子タスクの notes（背景・概要・完了条件）を読む
2. 親エピック notes（生課題・intake 時の文脈）を参照
3. [`planning-delivery.yaml`](../../../workflows/planning-delivery.yaml) に沿い委譲:
   - **issue-story-planner** — Handoff JSON（`output/planning/handoff/`）
   - **plan-reviewer** — PlanReviewResult（`output/planning/plan-review/`・必須）
   - **planning-pm（gate）** — 人間へ Handoff 要約提示・`handoff_approved` 取得
   - **asana-buddy** — `handoff_to_asana.py --require-review-result -y --if-not-exists`（既存親は **sync**：notes 更新 + 不足子作成）
4. 企画子の `done_when` を満たしたら **comment_task → complete_task -y → DeptWorkComplete**
5. **workflow-orchestrator** へ完了報告（残りの子タスク dispatch 委譲）

## Asana 記録（必須・順序）

```powershell
# 1. 署名付きコメント
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py --gid <子GID> --agent planning-pm --skill skills/planning/planning-pm/SKILL.md --summary "企画完了・Handoff Asana 投入済" --body "..." -y

# 2. 完了マーク
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\complete_task.py --gid <子GID> -y
```

- 委譲先（issue-story-planner / plan-reviewer）も**各自の slug**で `comment_task.py` を実行してから PM に報告すること。
- **`DeptWorkComplete` を出す前に** 1 → 2 の順で実行。
- フォーマット: [`docs/design/agent-asana-comment-signature.md`](../../../docs/design/agent-asana-comment-signature.md)

## gate（pm_gate 段階）

- `PlanReviewResult` で `review_passed` を確認（人間目視のみは不可）
- Handoff 要約（エピック名・子タスク一覧・レビュー status）を利用者に提示
- **`handoff_approved` を得てから** `handoff_to_asana.py` を実行する
- 差し戻し時は `handoff_plan` / `plan-reviewer` を再実行

### デフォルト（全 intake 経路 · opt-out）

1. Handoff 要約を利用者に提示
2. **同一セッションで** `handoff_to_asana.py --require-review-result -y --if-not-exists` を実行
3. 【承認】サブ・`--record-wait` は **作らない**

### opt-in planning gate（評価・監査）

トリガー（いずれか）: `--require-human-approval` · Handoff `meta.human_planning_approval: true` · env `ORG_OPS_PLANNING_APPROVAL_GATE=1` · epic notes `human_planning_approval: yes`

1. `create_planning_approval_gate.py --parent <親エピックGID> --handoff <path> -y`
2. `asana_ops_poller.py --record-wait <親> <【承認】サブGID> <URL>` — SuspendedSession 保存（**推奨 · 正規経路**）
3. **セッション終了** — `handoff_to_asana.py` は **RESUME 後**

`--record-wait` を省略した場合でも、Asana で【承認】complete 後は `org-ops-watch` が `HELPER source=wait_queue` で自動再開する（[`approval-flow.md`](../../../docs/design/approval-flow.md) §5.2）。ただし **opt-in 時は record-wait を省略しない**（監査・再現性のため）。

チャットの「承認」は **opt-in gate の RESUME 後**の再開合図として有効。**opt-in 時に【承認】サブ省略は不可。**

チェックリスト: [`workflow-orchestrator/SKILL.md`](../../platform/workflow-orchestrator/SKILL.md) **§H**（opt-in 時のみ）

## やらないこと

- 実行系子タスクの要件定義・実装（→ 開発チーム / UX チーム / 分析チーム）
- **`asana_execute` 直後に同一セッションで execution 系の成果物を書く**（→ task-dispatcher → 各 PM intake + ワーカー dispatch）
- Handoff JSON を他チームの入力として渡す（チーム間 I/O は **Asana notes**）
- ディスパッチ（→ task-dispatcher / 統括グループ）
- 新規 `skills/<organization>/<slug>/`（→ agent-creater）

## 成果物

| 種別 | 推奨パス |
|------|----------|
| Handoff | `output/planning/handoff/<theme>.json` |
| PlanReviewResult | `output/planning/plan-review/<theme>.json` |

## 出力

完了時: `DeptWorkComplete` JSON（[`schemas/dept-work-complete.v1.schema.json`](../../development/product-manager/schemas/dept-work-complete.v1.schema.json)）

## 起動例

```
planning-pm として子タスク GID 〈GID〉 を進めてください。
planning-delivery workflow に従い、Handoff 作成から Asana タスク化まで実行します。
```
