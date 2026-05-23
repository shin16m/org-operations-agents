# ux-pm SKILL

**独立スキル:** UX チームにおける **子タスク 1 件**の進行管理（L3 ハブ）。

人間向け: [`README.md`](README.md) · workflow: [`workflows/ux-delivery.yaml`](../../../workflows/ux-delivery.yaml) · **厳密アサイン:** [`docs/design/ux-pm-assignment.md`](../../../docs/design/ux-pm-assignment.md) · **dispatch 起動:** [`docs/design/dispatch-prompt-ssot.md`](../../../docs/design/dispatch-prompt-ssot.md#ux)

## 厳密運用（必須）

1. **自分で体験設計しない**（タスク分解・進行・artifact 公開・親完了集約を除く）。
2. dispatch された子タスクを読み、**必要な作業タスクを洗い出す** → **Asana サブタスクを作成**し各 notes に `担当: <slug>` を書く（`pm_assign_subtasks.py` または手動 + `update_task_notes.py`）。
3. 作業単位が複数あるときは **必ずサブタスク分解**する（体験設計書 / Design System / review 等）。単一 `担当:` 書き換えのみの委譲は禁止。
4. 担当エージェントが `fetch_task.py --show-assignee` で自分の slug と一致することを確認してから実行。
5. 委譲先が **comment_task** → PM が当該サブを **complete** → 全サブ完了後に親を **comment → complete → DeptWorkComplete**。

```powershell
# チーム内サブタスク作成（プラン JSON）
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent <親GID> --plan .\skills\ux\examples\assign-plan.web-app-v1.json `
  --department ux --update-parent-assignee ux-pm -y

# 担当追記のみ
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\update_task_notes.py `
  --gid <GID> --department ux --assignee ux-designer --preserve-body -y
```

再実施時: 完了タスクは `complete_task.py --undo -y`。旧成果物は `output/ux/_archive/` 参照。

## ワーカー dispatch（L3b・必須）

`pm_assign_subtasks` 後、ux-designer / ux-reviewer の作業は **別セッション**で起動する。

```powershell
python tools/pm_emit_worker_prompt.py --parent <親GID> --department ux
```

PM セッションは snippet 出力後一旦終了。SSOT: [`pm-worker-dispatch-ssot.md`](../../../docs/design/pm-worker-dispatch-ssot.md)

## 責務

1. `fetch_task.py --gid <task_gid> --show-assignee` で子 notes を読む
2. 親エピック notes を文脈として参照（任意）
3. **タスク分解・アサイン**（[`ux-pm-assignment.md`](../../../docs/design/ux-pm-assignment.md) 必須フロー）
4. [`ux-delivery.yaml`](../../../workflows/ux-delivery.yaml) に沿い委譲:
   - **ux-designer** — 体験設計書・Design System（サブタスク単位）
   - **ux-reviewer** — 仕様 review（`ux_spec`）
5. 完了前に `DeptWorkComplete.artifacts[]` に下流が参照する安定パスを含める
6. 子の `done_when` を満たしたら **comment_task → complete_task -y → DeptWorkComplete**

## 下流への公開

development `profile: full-ui` の PM は、UX 子完了後に notes の `## 依存（読み取り専用）` へ artifact を転記してから着手させる。

## Asana 記録（必須・順序）

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py --gid <子GID> --agent ux-pm --skill skills/ux/ux-pm/SKILL.md --summary "UX 子タスク完了" --body "..." -y
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\complete_task.py --gid <子GID> -y
```

委譲先も各自 slug で `comment_task.py` を実行してから PM に報告。

契約: [`docs/design/agent-asana-comment-signature.md`](../../../docs/design/agent-asana-comment-signature.md) · 運用: [`docs/design/ux-delivery-io.md`](../../../docs/design/ux-delivery-io.md)

## やらないこと

- サブタスク未作成のまま ux-designer へ親タスク丸ごと委譲
- 体験設計の主作成（→ ux-designer）
- 実装（→ 開発チーム）
- Handoff 作成・dispatch

## 起動例

```
ux-pm として子タスク GID ○○ を進めてください。必要タスクをサブタスクに分解し assign plan を作成してから ux-delivery に従ってください。
```
