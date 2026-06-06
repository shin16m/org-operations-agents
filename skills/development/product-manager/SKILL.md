# product-manager SKILL

**独立スキル:** 開発チームにおける **子タスク 1 件**の進行管理（L3 ハブ）。

人間向け: [`README.md`](README.md) · workflow: [`workflows/development-delivery.yaml`](../../../workflows/development-delivery.yaml) v3 · I/O: [`docs/design/development-delivery-io.md`](../../../docs/design/development-delivery-io.md) · **厳密アサイン:** [`docs/design/development-pm-assignment.md`](../../../docs/design/development-pm-assignment.md) · **dispatch 起動:** [`docs/design/dispatch-prompt-ssot.md`](../../../docs/design/dispatch-prompt-ssot.md#development)

## 厳密運用（必須）

1. **自分で実装しない**（タスク分解・profile 決定・進行・親完了集約を除く）。
2. dispatch された子タスクを読み、**delivery profile** を決め、**workflow フェーズをサブタスクに分解** → 各 notes に `担当: <slug>` を書く（`pm_assign_subtasks.py` または手動 + `update_task_notes.py`）。
3. **必須:** フェーズごとに **Asana サブタスク** を作成する。親タスクの `担当:` だけを書き換えて委譲することは禁止。
4. 担当エージェントが `fetch_task.py --show-assignee` で自分の slug と一致することを確認してから実行。
5. 委譲先が **comment_task** → PM が当該サブを **complete** → 全サブ完了後に親を **comment → complete → DeptWorkComplete**。

```powershell
# full-ui: ## 依存 転記後に gate（pm_assign 内でも自動チェック）
python tools/pm_intake_gate.py --gid <親GID> `
  --plan .\skills\development\examples\assign-plan.full-ui-v1.json

# チーム内サブタスク作成（プラン JSON）
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent <親GID> --plan .\skills\development\examples\assign-plan.full-ui-v1.json `
  --department development --update-parent-assignee product-manager -y

# 担当追記のみ
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\update_task_notes.py `
  --gid <GID> --department development --assignee tech-designer --preserve-body -y
```

再実施・差し戻し: **完了タスクを `--undo` しない**。review `failed` 時:

```powershell
python tools/pm_create_fix_subtask.py --parent <子GID> --review-json output/development/reviews/<file>.json -y
```

SSOT: [`pm-review-rework-ssot.md`](../../../docs/design/pm-review-rework-ssot.md)

## ワーカー dispatch（L3b・必須）

サブタスク作成後、**PM セッションで worker 作業を続けない。**

1. `python tools/pm_emit_worker_prompt.py --parent <親GID> --department development`
2. 出力された **WorkerDispatchSnippet** を利用者 / **別エージェントセッション**（requirements-writer, developer 等）へ渡す
3. **PM セッションは一旦終了**（ワーカー `comment_task` を待つ）
4. ワーカー完了後 PM が当該サブを `complete_task -y` → 次サブで 1 に戻る

SSOT: [`pm-worker-dispatch-ssot.md`](../../../docs/design/pm-worker-dispatch-ssot.md)

## 責務

1. `fetch_task.py --gid <task_gid> --show-assignee` で子 notes（背景・概要・完了条件・**profile**）を読む
2. 親エピック notes を文脈として参照（任意）
3. **タスク分解・アサイン**（[`development-pm-assignment.md`](../../../docs/design/development-pm-assignment.md) 必須フロー）
4. **delivery profile** を決定（省略時 `full`）:
   - `full` — 非 UI
   - **`full-ui`** — UX `## 依存` 必須 + ux_implementation サブタスク
   - `lite` — 設計 skip（**非 UI のみ**）
   - `doc-only` — 実装 skip
5. [`development-delivery.yaml`](../../../workflows/development-delivery.yaml) に沿い委譲（**各フェーズはサブタスク単位**）:
   - **requirements-writer** — 要件 / 事後仕様（mode 指定）
   - **tech-designer** — 技術設計（full-ui は UX 仕様を引用）
   - **developer** — 実装・修正
   - **dev-reviewer** — 要件・設計・コード・mismatch レビュー
   - **ux-reviewer** — 実装 UI 一致（`full-ui` のみ）
   - **qa-verifier** — 動作検証
6. `MismatchReviewResult.fix_target == code` 時: **developer 向け修正サブ**を新規作成 → L3b dispatch
7. 各 review / verification で `failed`: **修正サブ** → 修正後 **再 review サブ**を新規追加（[`pm-review-rework-ssot.md`](../../../docs/design/pm-review-rework-ssot.md)）
8. 子の `done_when` を満たしたら **comment_task → complete_task -y → DeptWorkComplete**

### md 成果物の Asana 添付（必須）

| フェーズ | 添付対象 | 確認 |
|----------|----------|------|
| requirements | `output/development/requirements/<PM子GID>-requirements.md` | **worker サブ** + **要件 review サブ**の両方に attach 済み |
| as-built-spec | `output/development/specs/<PM子GID>-spec.md` | **worker サブ** + **mismatch review サブ**の両方に attach 済み（workflow に spec がある profile） |

- worker 完了前: requirements-writer が `attach_task_files.py --gid <worker> --also-gid <review_sub> --skip-if-present` を実行
- PM が worker サブを **complete する前**に worker / review 各 `--list` でファイル名一致を確認

## Asana 記録（必須・順序）

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py --gid <子GID> --agent product-manager --skill skills/development/product-manager/SKILL.md --summary "子タスク完了" --body "..." -y
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\complete_task.py --gid <子GID> -y
```

委譲先も各自 slug で `comment_task.py` を実行してから PM に報告する。

## やらないこと

- Handoff 新規作成（→ 企画チーム）
- Handoff JSON をチーム間入力として読む
- ディスパッチ（→ task-dispatcher）
- 新規 `skills/<organization>/<slug>/`（→ agent-creater）
- **ワーカー役の成果物作成** — 要件・設計・コード・レビュー JSON（[`development-pm-assignment.md`](../../../docs/design/development-pm-assignment.md)「PM が書いてはいけない成果物」）
- **`output/development/app/` への直接実装**（Streamlit 等 — → developer サブタスク）
- **サブタスク未作成のまま** workflow フェーズを自分で実行すること
- `development-delivery.yaml` の worker step（requirements-writer / developer 等）を PM セッションで代行すること

intake 完了前チェック:

- [ ] `pm_assign_subtasks.py` 実行済み（または同等の nested サブ作成）
- [ ] 親 notes `担当: product-manager`
- [ ] 各サブ notes に `担当: <worker slug>`

未達なら **成果物を書かず** サブタスク分解から開始する。

## 成果物パス

| 種別 | パス |
|------|------|
| 要件 | `output/development/requirements/<task_gid>-requirements.md` |
| 設計 | `output/development/design/<task_gid>-design.md` |
| 事後仕様 | `output/development/specs/<task_gid>-spec.md` |
| レビュー | `output/development/reviews/` |
| Asana 添付 | [`attach_task_files.py`](../../platform/asana-buddy/optional/attach_task_files.py) — requirements / spec md を worker サブへ |

## 起動例

```
product-manager: 子タスク GID ○○ を profile=full-ui で development-delivery v3 に従い進めてください。
pm_assign_subtasks でフェーズ分解し、UX 依存は notes ## 依存 を確認してください。
```
