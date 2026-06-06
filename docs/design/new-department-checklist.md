# 新チーム（department）追加チェックリスト

新規 **L3 チーム** または **dispatch 対象 department** を足すとき、[`department-model.md`](department-model.md) の 4 点セットに加え、本チェックリストを **すべて** 確認する。漏れ防止用。

**機械チェック（PR 前）:**

```powershell
python tools/validate_org_registry.py
python tools/validate_ssot_contract.py
python tools/check_new_department.py --department <id>   # 個別
python tools/check_new_department.py --all                # 全 enabled
python tools/check_new_skill.py --slug <新slug> --department <id>   # ロール追加時
python tools/check_new_skill.py --all-enabled             # 全 enabled slug
```

`check_new_department.py` は **A〜J の必須行**を機械チェックする。`check_new_skill.py` は **単一 slug の配線**を検証する。手動チェックの前に必ず実行。

---

## A. コア（必須 4 点 + registry）

| # | 成果物 | 確認 |
|---|--------|------|
| A1 | [`workflows/organizations.yaml`](../../workflows/organizations.yaml) | `departments[]` 1 行 · `pillar_defaults`（任意） |
| A2 | `workflows/<id>-delivery.yaml` | `entry_agent` · `assignment_doc`（PM 厳密運用がある場合） |
| A3 | `docs/design/<id>-delivery-io.md` | チーム内 I/O · チーム間 I/O · ゲート · やらないこと |
| A4 | `skills/<dept>/<pm-slug>/` | PM ハブ SKILL · README |
| A5 | [`workflows/agent-registry.yaml`](../../workflows/agent-registry.yaml) | PM + ワーカー + reviewer · `enabled: true` |
| A6 | ワーカー SKILL | `skills/<dept>/<slug>/` 各ロール |

---

## B. スキーマ（department enum 同期）

| # | ファイル |
|---|----------|
| B1 | [`dispatch-request.v1.schema.json`](../../skills/platform/task-dispatcher/schemas/dispatch-request.v1.schema.json) |
| B2 | [`dept-work-complete.v1.schema.json`](../../skills/development/product-manager/schemas/dept-work-complete.v1.schema.json) |
| B3 | [`asana-buddy-handoff.v1.2.schema.json`](../../skills/planning/issue-story-planner/schemas/asana-buddy-handoff.v1.2.schema.json) |

→ **`python tools/validate_org_registry.py`** で三つと organizations.yaml が一致すること。

---

## C. チーム間 SSOT（ドキュメント）

| # | ファイル | 追記内容 |
|---|----------|----------|
| C1 | [`dept-work-io.md`](dept-work-io.md) | `DispatchRequest.department` · PM 完了担当 · レビュー Result 型 · 署名ロール |
| C2 | [`handoff-v12-department.md`](handoff-v12-department.md) | department 値表に 1 行 |
| C3 | [`team-conventions.md`](team-conventions.md) | 比較表に列追加 · チーム節 |
| C4 | [`department-model.md`](department-model.md) | 責務表 · I/O 一覧 · 配賦順序（§三層レイヤーと配賦） |
| C5 | [`task-dispatcher/SKILL.md`](../../skills/platform/task-dispatcher/SKILL.md) | ルーティング表 · department enum |
| C6 | [`workflow-orchestrator/SKILL.md`](../../skills/platform/workflow-orchestrator/SKILL.md) | dispatch 順序（必要なら） |
| C7 | [`issue-story-planner/SKILL.md`](../../skills/planning/issue-story-planner/SKILL.md) | `subtasks[].department` · Handoff チェックリスト |
| C8 | [`dispatch-workflow.md`](../e2e/dispatch-workflow.md) | E2E 手順 |
| C9 | [`skills-inventory.md`](../inventory/skills-inventory.md) | スキル一覧 |
| C10 | [`skills/README.md`](../../skills/README.md) | 組織フォルダ表 |
| C11 | ルート [`README.md`](../../README.md) | スキル一覧 · dispatch 図 |
| C12 | [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md) | department 節 + pm_assign 必須 |

---

## D. PM 厳密運用（分析チーム同等が必要な場合）

| # | 成果物 |
|---|--------|
| D1 | `docs/design/<id>-pm-assignment.md` — サブタスク分解必須 · CLI · `--show-assignee` · [review NG → 修正タスク](pm-review-rework-ssot.md) |
| D1b | [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md) — 該当 department 節を追加 |
| D2 | PM SKILL — 「厳密運用（必須）」節 |
| D3 | ワーカー SKILL — 着手前 `fetch_task --show-assignee` |
| D4 | `skills/<dept>/examples/assign-plan.*.json` — サブタスクプラン例 |
| D5 | [`pm_assign_subtasks.py`](../../skills/platform/asana-buddy/optional/pm_assign_subtasks.py) — `--department` 対応確認 |
| D6 | `docs/verification/<id>/<id>-delivery-dryrun.md`（または `tools/run_*_<id>_dryrun.py`）

---

## E. 企画・Handoff

| # | 成果物 |
|---|--------|
| E1 | `skills/planning/issue-story-planner/examples/handoff.<theme>.json` — 新 department の subtask 例 |
| E2 | plan-reviewer / gate 用 Handoff が v1.2 + department 付き |

---

## F. 全体仕様（エージェント構成）

| # | ファイル |
|---|----------|
| F1 | [`team-conventions.md`](team-conventions.md) — 四チーム比較・I/O 索引 |
| F2 | [`workflows/agent-registry.yaml`](../../workflows/agent-registry.yaml) — 全 slug 登録 |
| F3 | [`docs/inventory/skills-inventory.md`](../inventory/skills-inventory.md) — スキル棚卸し |

---

## G. 下流連携（他チームが consume する場合）

| # | 内容 |
|---|------|
| G1 | [`department-model.md`](department-model.md) — 成果物共有フロー例 |
| G2 | 下流チーム `*-delivery-io.md` — `## 依存（読み取り専用）` 必須条件 |
| G3 | 下流 PM assignment — 横断 reviewer 委譲手順（サブタスク化） |

---

## H. 横断 reviewer（他チーム PM から委譲されるロール）

| # | 内容 |
|---|------|
| H1 | reviewer SKILL — 委譲元 PM 両方を明記 |
| H2 | 開発 / 他 PM assignment — サブタスク + `担当: <reviewer>` |
| H3 | [`agent-asana-comment-signature.md`](agent-asana-comment-signature.md) — 署名対象ロール |

---

## I. delivery 強みの型（L3 · 開発 v3 同等を目指す場合）

| # | 成果物 |
|---|--------|
| I1 | [`delivery-strength-pattern.md`](delivery-strength-pattern.md) — 適用マトリクスに 1 行 |
| I2 | profile 選定（必要なら）· PM/worker 分離 · 多段ゲート |
| I3 | 下流 consume がある場合 [`cross-team-artifact-bridge.md`](cross-team-artifact-bridge.md) |

---

## J. スキル × ペルソナ

| # | 成果物 |
|---|--------|
| J1 | [`skill-persona-principles.md`](skill-persona-principles.md) — SKILL / persona 分離 |
| J2 | [`docs/inventory/skill-persona-matrix.md`](../inventory/skill-persona-matrix.md) — 全 slug 行追加 |
| J3 | 各 `personas/*.md` に **志向** 行 |

---

## 完了条件

- [ ] `python tools/validate_org_registry.py` が exit 0
- [ ] `python tools/check_new_department.py --department <id>` が exit 0
- [ ] 新規 slug 追加時 `python tools/check_new_skill.py --slug <slug>` が exit 0
- [ ] 本チェックリスト A〜J の該当行にチェック
- [ ] dry-run 文書または `tools/run_*dryrun*.py` 1 本

---

## 参照

- 4 点セット: [`department-model.md`](department-model.md)
- 強みの型: [`delivery-strength-pattern.md`](delivery-strength-pattern.md)
- 分析 PM 厳密運用の参照実装: [`analytics-pm-assignment.md`](analytics-pm-assignment.md)
- UX PM 厳密運用: [`ux-pm-assignment.md`](ux-pm-assignment.md)
- ロール追加: [`CONTRIBUTING.md`](../../CONTRIBUTING.md)
