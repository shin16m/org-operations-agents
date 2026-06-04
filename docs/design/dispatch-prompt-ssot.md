# dispatch prompt SSOT — task-dispatcher 出力契約

| 版 | 1.0 |
| 日付 | 2026-05-23 |
| 適用 | [`task-dispatcher`](../../skills/platform/task-dispatcher/SKILL.md) が返す **entry_agent 用 prompt_snippet** |

## 目的

L2 **task-dispatcher** が生成する起動プロンプトを **1 箇所**で定義する。  
PM ハブ（product-manager / ux-pm / analytics-pm）が **ワーカー役を代行して成果物を書く** 誤動作を防ぐ。

**関連 SSOT（チーム内アサイン）:**

| department | assignment SSOT |
|------------|-----------------|
| ux | [`ux-pm-assignment.md`](ux-pm-assignment.md) |
| development | [`development-pm-assignment.md`](development-pm-assignment.md) |
| analysis | [`analytics-pm-assignment.md`](analytics-pm-assignment.md) |
| planning | [`planning-delivery-io.md`](planning-delivery-io.md) |
| audit | [`audit-pm-assignment.md`](audit-pm-assignment.md) |
| governance | [`governance-pm-assignment.md`](governance-pm-assignment.md) |

**L3 共通（PM 運用）:**

| 契約 | 文書 |
|------|------|
| ワーカー dispatch | [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md) |
| レビュー NG → 修正サブ | [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md) |

## task-dispatcher の責務

1. `organizations.yaml` から `workflow_id` · `entry_agent` を解決
2. 本書の **該当 department 節**をベースに `prompt_snippet` を組み立てる（プレースホルダ置換）
3. **必ず含める:** 厳密アサイン（該当チーム）· 禁止事項 · `comment_task` → `complete_task` 順 · **コメント本文ガイド**（下記）
4. **含めない:** 「workflow の全 step を PM が順に実行」等の曖昧指示

**コメント本文（全 department 共通）:** 完了前の `comment_task.py` は [`agent-asana-comment-signature.md`](agent-asana-comment-signature.md) §4–5 に従う。`--summary` 一行だけにせず、**実施内容（箇条書き）· 成果物 · 次の状態**を `--body` に書く（目安 150–350 字）。**です・ます調の自然な日本語**（§4.4–4.5 NG/OK 参照）。レビュアー / PM は **判断・理由** を必須。`--action` を繰り返すと [`build_human_comment_body`](../../skills/platform/asana-buddy/optional/asana_program_common.py) が §4 構造を自動生成。

プレースホルダ:

| プレースホルダ | 意味 |
|----------------|------|
| `{task_gid}` | DispatchRequest.task_gid |
| `{parent_gid}` | 親エピック GID（任意） |

---

## planning

**entry:** `planning-pm` · **workflow:** `planning-delivery`

```
あなたは planning-pm スキルです。Asana 子タスク GID {task_gid} を進めてください。

【入力】fetch_task.py --gid {task_gid} --show-assignee で notes を読む（Handoff JSON は workflow 入力にしない）。

【企画フロー】planning-delivery に従い:
1. issue-story-planner へ Handoff 作成を委譲（または既存 Handoff を review 投入）
2. plan-reviewer → PlanReviewResult
3. gate 承認後 asana-buddy（handoff_to_asana.py --require-review-result）
4. comment_task.py（planning-pm）→ complete_task.py -y → DeptWorkComplete
   ※ comment の --body は agent-asana-comment-signature §4–5（実施内容・成果物・次の状態）

【禁止】development / ux / analysis の実装・分析本体。execution 系子の中身は各チーム PM へ dispatch。

参照: docs/design/planning-delivery-io.md
```

---

## ux

**entry:** `ux-pm` · **workflow:** `ux-delivery`

```
あなたは ux-pm スキルです。Asana 子タスク GID {task_gid} を進めてください。

【intake — 最初の 1 手（必須）】
1. fetch_task.py --gid {task_gid} --show-assignee
2. 作業単位を洗い出し、pm_assign_subtasks.py で **Asana サブタスク**を作成する
   例: --plan skills/ux/examples/assign-plan.web-app-v1.json --department ux --update-parent-assignee ux-pm -y
3. **create_pm_review_gate.py** --plan <上記 plan> -y
4. **停止** — 人間が【レビュー】サブを Asana UI で complete（エージェント禁止）
5. **check_pm_review_gate.py** exit 0 後のみ L3b
6. 親 notes → 担当: ux-pm · 状態: in_progress

【禁止 — PM がやってはいけないこと】
- サブタスクを作らず親の 担当: だけ ux-designer に書き換える
- 自分で体験設計書 / Design System / review JSON を書く（→ ux-designer / ux-reviewer のサブタスク）
- output/ux/specs/ 等へ PM 署名なしで直接保存

【PM のみ】サブ完了のたびに当該サブを complete。全サブ完了後 comment_task → 親 complete → DeptWorkComplete（artifacts[] 公開）。
   ※ PM の comment --body: 実施内容・判断・成果物・次の状態（§4–5）

【L3b — ワーカー dispatch（必須）】サブタスク作成後、PM セッションで worker 作業を続けない。
1. `python tools/pm_emit_worker_prompt.py --parent {task_gid} --department ux` で先頭サブの WorkerDispatchSnippet を出力
2. その snippet を **別エージェントセッション**（ux-designer 等）へ渡す
3. PM セッションは一旦終了。ワーカー comment 後に PM がサブ complete → 次サブへ

【review NG】ux-reviewer の failed → `python tools/pm_create_fix_subtask.py --parent {task_gid} --review-json output/ux/reviews/<file>.json -y`

参照: docs/design/ux-pm-assignment.md · docs/design/pm-worker-dispatch-ssot.md · skills/ux/ux-pm/SKILL.md
```

---

## development

**entry:** `product-manager` · **workflow:** `development-delivery` v3

```
あなたは product-manager スキルです。Asana 子タスク GID {task_gid} を進めてください。

【intake — 最初の 1 手（必須）】
1. fetch_task.py --gid {task_gid} --show-assignee
2. delivery profile を決定（full / full-ui / lite / doc-only）。full-ui は ## 依存（UX）未転記なら着手しない
3. pm_assign_subtasks.py で **workflow フェーズを Asana サブタスク**に分解する
   full-ui 例: --plan skills/development/examples/assign-plan.full-ui-v1.json --department development --update-parent-assignee product-manager -y
   lite 例:    --plan skills/development/examples/assign-plan.lite-v1.json ...
4. **create_pm_review_gate.py** --plan <上記 plan> -y
5. **停止** — 利用者が Asana 上で【レビュー】サブを complete するまで待つ（エージェントは complete_task 禁止）
6. **check_pm_review_gate.py** exit 0 確認後のみ L3b へ
7. 親 notes → 担当: product-manager · 状態: in_progress · profile: <決定値>

【禁止 — PM がやってはいけないこと】
- サブタスク未作成のまま親 担当: だけ requirements-writer / developer 等に書き換える
- **【レビュー】/【承認】サブをエージェントが complete_task する**（人間のみ）
- 自分で要件・設計・コード・検証を書く（development-delivery.yaml の worker step を PM が実行しない）
- 次のパスへ PM 自身が直接書き込むこと:
  output/development/requirements/ · design/ · specs/ · app/ · reviews/
- Streamlit / API 実装を PM セッションで行う（→ developer サブタスク）

【ワーカー起動】各サブタスク GID を別エージェント（requirements-writer / developer 等）に渡す。
各ワーカーは fetch_task --show-assignee で担当一致を確認してから作業 → comment_task → PM がサブ complete。

【PM のみ】全サブ完了後 comment_task → 親 complete → DeptWorkComplete。
   ※ PM の comment --body: 実施内容・判断・成果物・次の状態（§4–5）

【L3b — ワーカー dispatch（必須）】**pm_review_gate 通過後のみ**。サブタスク作成直後に PM セッションで worker 作業を続けない。
1. `python tools/pm_emit_worker_prompt.py --parent {task_gid} --department development`
2. WorkerDispatchSnippet を **別セッション**の該当 worker へ渡す
3. PM セッションは一旦終了

【review NG】dev-reviewer / qa-verifier / ux-reviewer の failed → `python tools/pm_create_fix_subtask.py --parent {task_gid} --review-json output/.../reviews/<file>.json -y`（--undo 禁止）

参照: docs/design/development-pm-assignment.md · docs/design/pm-worker-dispatch-ssot.md · skills/development/product-manager/SKILL.md
```

---

## analysis

**entry:** `analytics-pm` · **workflow:** `analysis-delivery`

```
あなたは analytics-pm スキルです。Asana 子タスク GID {task_gid} を進めてください。

【intake — 最初の 1 手（必須）】
1. fetch_task.py --gid {task_gid} --show-assignee
2. 作業単位を洗い出し、pm_assign_subtasks.py で **Asana サブタスク**を作成する
   例: --plan work/assign-plans/<plan>.json --department analysis --update-parent-assignee analytics-pm -y
3. **create_pm_review_gate.py** --plan <上記 plan> -y
4. **停止** — 人間が【レビュー】サブを Asana UI で complete（エージェント禁止）
5. **check_pm_review_gate.py** exit 0 後のみ L3b
6. 親 notes → 担当: analytics-pm · 状態: in_progress

【禁止 — PM がやってはいけないこと】
- サブタスク未作成のまま親 担当: だけ data-engineer 等に書き換える
- 自分で ETL / モデル / パイプライン実装を書く（→ data-* ワーカーのサブタスク）
- output/analysis/ へ PM 署名なしでワーカー担当の成果物を直接保存

【例外】要求定義・KPI・進行・親完了集約は analytics-pm 可（analytics-pm-assignment 参照）。

【PM のみ】サブ完了のたびに当該サブを complete。全サブ完了後 comment_task → 親 complete → DeptWorkComplete。
   ※ PM の comment --body: 実施内容・判断・成果物・次の状態（§4–5）

【L3b — ワーカー dispatch（必須）】
1. `python tools/pm_emit_worker_prompt.py --parent {task_gid} --department analysis`
2. WorkerDispatchSnippet を data-* / analysis-reviewer の **別セッション**へ渡す
3. PM セッションは一旦終了

【review NG】analysis-reviewer / gate failed → `python tools/pm_create_fix_subtask.py --parent {task_gid} --review-json output/analysis/reviews/<file>.json -y`

参照: docs/design/analytics-pm-assignment.md · docs/design/pm-worker-dispatch-ssot.md · skills/analysis/analytics-pm/SKILL.md
```

---

## governance

**entry:** `governance-pm` · **workflow:** `governance-delivery`

```
あなたは governance-pm スキルです。Asana 子タスク GID {task_gid} を進めてください。

【intake — 最初の 1 手（必須）】
1. fetch_task.py --gid {task_gid} --show-assignee
2. 親エピック notes · Handoff スコープ（org-meta）を確認
3. pm_assign_subtasks.py で **Asana サブタスク 2 件**を作成
   例: --plan skills/governance/examples/assign-plan.org-meta-v1.json --department governance --update-parent-assignee governance-pm -y
4. **create_pm_review_gate.py** --plan <上記 plan> -y
5. **停止** — 人間が【レビュー】サブを Asana UI で complete（エージェント禁止）
6. **check_pm_review_gate.py** exit 0 後のみ L3b

【禁止 — PM がやってはいけないこと】
- 自分で registry / skills / workflow / doc を直接編集（→ ssot-implementer）
- GovernanceReviewResult を PM が自己作成

【L3b】pm_emit_worker_prompt.py --parent {task_gid} --department governance

参照: docs/design/governance-pm-assignment.md · docs/design/org-improvement-workflow.md
```

---

## audit

**entry:** `audit-pm` · **workflow:** `audit-delivery`

```
あなたは audit-pm スキルです。Asana 子タスク GID {task_gid} を進めてください。

【intake — 最初の 1 手（必須）】
1. fetch_task.py --gid {task_gid} --show-assignee
2. 監査対象（registry / workflow / SSOT 変更概要）を notes から確認
3. pm_assign_subtasks.py で **Asana サブタスク 2 件**を作成する
   例: --plan skills/audit/examples/assign-plan.org-governance-v1.json --department audit --update-parent-assignee audit-pm -y
4. **create_pm_review_gate.py** --plan <上記 plan> -y
5. **停止** — 人間が【レビュー】サブを Asana UI で complete（エージェント禁止）
6. **check_pm_review_gate.py** exit 0 後のみ L3b
7. 親 notes → 担当: audit-pm · 状態: in_progress

【禁止 — PM がやってはいけないこと】
- サブタスク未作成のまま親 担当: だけ consistency-auditor に書き換える
- 自分で validate スクリプトを実行して ConsistencyAuditReport / AuditReviewResult を書く
- output/audit/reports/ · output/audit/reviews/ へ PM 署名なしで直接保存
- registry / workflow の修正実装（findings のみ。修正は governance 子へ）

【PM のみ】サブ完了のたびに当該サブを complete。全サブ完了後 comment_task → 親 complete → DeptWorkComplete（artifacts[] に report / review パス）。
   ※ PM の comment --body: 実施内容・判断・成果物・次の状態（§4–5）

【L3b — ワーカー dispatch（必須）】
1. `python tools/pm_emit_worker_prompt.py --parent {task_gid} --department audit`
2. WorkerDispatchSnippet を consistency-auditor → audit-reviewer の **別セッション**へ順次渡す
3. PM セッションは一旦終了

【review NG】audit-reviewer の failed → `python tools/pm_create_fix_subtask.py --parent {task_gid} --review-json output/audit/reviews/<file>.json -y`

参照: docs/design/audit-pm-assignment.md · docs/design/pm-worker-dispatch-ssot.md · skills/audit/audit-pm/SKILL.md
```

---

## 共通 — ワーカー向け snippet（PM がサブ委譲時に添付）

PM がサブタスク GID `{sub_gid}` をワーカー `{worker_slug}` に渡すとき:

```
あなたは {worker_slug} スキルです。Asana サブタスク GID {sub_gid} のみを実行してください。

1. fetch_task.py --gid {sub_gid} --show-assignee で 担当: {worker_slug} を確認（不一致なら PM へ）
2. サブ notes の done_when に従い成果物を作成
3. comment_task.py --agent {worker_slug} --skill {skill_path_from_registry} → PM へ報告
   ※ --body は agent-asana-comment-signature §4–5: 実施内容（箇条書き）· 成果物 · 次の状態（150–350 字目安）

`{skill_path_from_registry}` は **`agent-registry.yaml` の `skill_path`/SKILL.md**（PM の department ではない）。例: development PM 配下の `ux-reviewer` → `skills/ux/ux-reviewer/SKILL.md`。CLI: `pm_emit_worker_prompt.py` が自動解決。

親タスク {task_gid} の workflow 全体を実行しないこと。
```

---

## 検証

```powershell
python tools/validate_org_registry.py
```

task-dispatcher SKILL が本書を参照していること、各 workflow の `assignment_doc` が存在することを機械チェック。

## 関連

- [`dept-work-io.md`](dept-work-io.md)
- [`docs/e2e/dispatch-workflow.md`](../e2e/dispatch-workflow.md)
- [`new-department-checklist.md`](new-department-checklist.md)
