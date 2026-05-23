# ワークフロー I/O 契約・ゲート・オーケストレーター責務

registry / workflow 実体は [`workflows/`](../../workflows/)。セッション状態は [`workflow-session-io.md`](workflow-session-io.md)。

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

## エージェント進行（L1）

- **intake 担当**は bootstrap → dispatch（企画チーム）まで同一セッションで進める。
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
  O->>D: dispatch dev/analysis 子
```

## 移行（v2 → v3）

v2 では L1 に plan / review / gate / execute があった。**v3 から企画は planning-delivery（L3）** で実行する。

## 新規 SKILL 実体

**agent-creater 経由のみ**（[`skills-inventory.md`](../inventory/skills-inventory.md) 参照）。
