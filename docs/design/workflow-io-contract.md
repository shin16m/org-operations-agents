# ワークフロー I/O 契約・ゲート・オーケストレーター責務

registry / workflow 実体は [`workflows/`](../../workflows/)。セッション状態は [`workflow-session-io.md`](workflow-session-io.md)。

**パイプライン図・段階一覧の SSOT は本ファイル。** README / CONTRIBUTING / SKILL / Cursor rule はここを参照し、同じ ASCII 図をコピーしない。

## 標準パイプライン（default v3 · SSOT）

```
workflow-orchestrator（intake → bootstrap → dispatch）
  → planning-pm（企画チーム / planning-delivery）
    → issue-story-planner → plan-reviewer（必須）
    → planning-pm（gate）→ asana-buddy
  → task-dispatcher（execution 系子ごと）
  → 各 PM: pm_assign_subtasks → **pm_review_gate（人間 · Asana dependencies）** → L3b worker dispatch
  → ux-pm → ux-designer / ux-reviewer
  → product-manager → requirements-writer / …
  → analytics-pm → data-architect / …
  → governance-pm → ssot-implementer / governance-reviewer
  → audit-pm → consistency-auditor / audit-reviewer（組織変更エピックの **最後**）
```

- L1 定義: [`workflows/default.yaml`](../../workflows/default.yaml) v3
- 企画 L3: [`workflows/planning-delivery.yaml`](../../workflows/planning-delivery.yaml)
- 組織ルーティング: [`workflows/organizations.yaml`](../../workflows/organizations.yaml)
- 手順（コマンド例）: [`docs/e2e/default-workflow.md`](../e2e/default-workflow.md)

## 段階とスロット（default v3）

| 段階 ID | スロット | 担当スキル | 入力 | 出力 |
|---------|----------|------------|------|------|
| `intake` | orchestrate | workflow-orchestrator | 生課題（自然言語） | bootstrap 用最小 Handoff |
| `bootstrap` | execute | asana-buddy | bootstrap Handoff | Asana 親 + 企画子 1 件 |
| `dispatch` | dispatch | task-dispatcher | DispatchRequest（planning） | planning-pm 用 prompt_snippet |

## 企画チーム L3（planning-delivery）

| 段階 ID | スロット | 担当 | 入力 | 出力 |
|---------|----------|------|------|------|
| `handoff_plan` | dept_work | issue-story-planner | 生課題 + 子 notes | `AsanaBuddyHandoff` |
| `plan_review` | dept_review | plan-reviewer | Handoff 案 | `PlanReviewResult` |
| `pm_gate` | dept_orchestrate | planning-pm | Handoff + PlanReviewResult | execute 可否 |
| `asana_execute` | execute | asana-buddy | 承認済み Handoff | Asana 親更新 + 実行系子 |

## ゲート（企画チーム内）

| ゲート ID | 条件 | 未達時 |
|-----------|------|--------|
| `review_passed` | **`plan-reviewer` 必須。** `PlanReviewResult.status` が `passed` または `passed_with_notes` | `asana_execute` 不可。差し戻しは `handoff_plan` |
| `handoff_approved` | `review_passed` 済みのうえ、人間が planning-pm（pm_gate）経由で **Asana タスク作成** を明示承認 | `handoff_to_asana.py` を実行しない |

## asana_execute 後（execution 系 — 必須分離）

`handoff_to_asana.py`（`--require-review-result`）で execution 系子が Asana に存在した**後**:

| 禁止 | 正規 |
|------|------|
| 同一セッションで development / ux / analysis の **成果物・doc 更新**に着手 | [`task-dispatcher`](../../skills/platform/task-dispatcher/SKILL.md) → 各 PM **intake** |
| product-manager / ux-pm / analytics-pm が **ワーカー役を代行** | `pm_assign_subtasks` → **`pm_review_gate`（人間 · dependencies）** → **L3b** worker dispatch（[`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md)） |
| gate 承認を「実装開始の合図」とみなす | 企画 PM は **comment → complete → DeptWorkComplete** まで。実行系は別 dispatch |

org-ops メタ doc のみの開発子は **profile: doc-only**（[`assign-plan.org-meta-doc-v1.json`](../../skills/development/examples/assign-plan.org-meta-doc-v1.json)）。本体を PM が先行完了した場合の事後補完: [`docs/verification/asana-comment-detail-delivery.md`](../verification/asana-comment-detail-delivery.md)。

**PM review gate（execution）:** [`pm-assign-review-gate.md`](pm-assign-review-gate.md) · planning gate との違い: [`planning-gate-vs-pm-review-gate.md`](planning-gate-vs-pm-review-gate.md)

**Asana ドリブン運用（Phase 1–4）:** [`asana-driven-ops.md`](asana-driven-ops.md) — スキャン intake · planning gate Asana 化 · 保留再開 · **Phase 4:** auto-intake SSOT · `--record-wait` ダッシュボード必須（`asana_ops_poller` / `check_workflow_suspend` · [`workflow-session-io.md`](workflow-session-io.md) SuspendedSession）。**gate 到達時チェックリスト:** [`workflow-orchestrator/SKILL.md`](../../skills/platform/workflow-orchestrator/SKILL.md) §H

**タスク / エピックレトロ（親 complete 前）:** [`task-retrospective-ssot.md`](task-retrospective-ssot.md) — 各 complete 前レトロ · audit 後集約 · 依頼者承認 → intake 起票

**配賦順（execution 系）:** ux → development / analysis → **`audit`（組織変更時・親 complete 直前）**。監査は他 execution 子完了後に dispatch する（[`audit-delivery-io.md`](audit-delivery-io.md)）。

## エージェント進行（L1）

- **intake 担当**は bootstrap → dispatch（企画チーム）まで同一セッションで進める。
- **和久桶さん（workflow-orchestrator）への相談**も intake から。メタ変更（新 department · registry 等）を **gate 前に直接実装しない**（[`workflow-orchestrator/SKILL.md`](../../skills/platform/workflow-orchestrator/SKILL.md)）。
- **企画 gate** は planning-pm が担当（L1 orchestrator から移管）。

## orchestrator の役割（v3）

| step | 役割 |
|------|------|
| `intake` | 課題受付。利用者の**唯一の入口** |
| `bootstrap` | 最小 Asana（企画子 1 件） |
| `dispatch` | 企画チームへ初回配賦；完了後は execution 系子を順次配賦 |

## 変更境界（新規スキル追加時）

| 変更するもの | 誰が | 内容 |
|--------------|------|------|
| `skills/<organization>/<slug>/` 実体 | **agent-creater のみ** | README, SKILL, personas, optional |
| `workflows/agent-registry.yaml` | 人間（PR） | slug, slot, I/O 参照, enabled |
| `workflows/*.yaml` | 人間（PR） | 段階・agent 参照・ゲート |
| 個別 SKILL.md | agent-creater 生成後に調整 | スロット固有ロジック |

## シーケンス（default v3）

```mermaid
sequenceDiagram
  participant U as 利用者
  participant O as workflow-orchestrator
  participant A as asana-buddy
  participant D as task-dispatcher
  participant PM as planning-pm
  participant P as issue-story-planner
  participant R as plan-reviewer

  U->>O: 生課題（intake）
  O->>A: bootstrap Handoff
  A-->>O: 親+企画子 GID
  O->>D: dispatch planning
  D->>PM: prompt_snippet
  PM->>P: Handoff 作成
  P-->>PM: Handoff 案
  PM->>R: レビュー
  R-->>PM: PlanReviewResult
  PM->>U: gate（要約・承認）
  U->>PM: handoff_approved
  PM->>A: handoff_to_asana
  A-->>PM: Asana 更新
  PM-->>O: DeptWorkComplete
  O->>D: dispatch ux/dev/analysis 子
```

## 移行（v2 → v3）

v2 では L1 に plan / review / gate / execute があった。**v3 から企画は planning-delivery（L3）** で実行する。

## 新規 SKILL 実体

**agent-creater 経由のみ**（[`skills-inventory.md`](../inventory/skills-inventory.md) 参照）。
