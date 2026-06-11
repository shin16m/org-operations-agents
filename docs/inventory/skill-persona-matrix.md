# スキル × ペルソナ対応表

| 版 | 1.0 |
| 日付 | 2026-06-06 |
| 原則 | [`skill-persona-principles.md`](../design/skill-persona-principles.md) |
| 登録 SSOT | [`workflows/agent-registry.yaml`](../../workflows/agent-registry.yaml) |

## 動き方（2層）

```
人間 / dispatch
    │
    ▼
1. slug 特定（Asana notes の 担当:）
2. SKILL.md を読む → 何をするか（契約）
3. persona.md を読む → どう振る舞うか（志向）
4. 成果物作成 → comment_task → PM complete
```

| 層 | ファイル | 役割 |
|----|----------|------|
| **SKILL** | `skills/<team>/<slug>/SKILL.md` | I/O・手順・パス・ゲート・やらないこと |
| **persona** | `skills/<team>/<slug>/personas/*.md` | ミッション・**志向**・協調 |
| **registry** | `workflows/agent-registry.yaml` | slug → skill_path・slot |

**PM と worker:** PM の SKILL は分解・委譲・完了のみ。worker は **別セッション（L3b）** で SKILL + persona に従う。

---

## 統括グループ（platform）

| slug | slot | persona | 要点 |
|------|------|---------|------|
| `workflow-orchestrator` | orchestrate | `workflow_orchestrator.md` | 配線のみ |
| `task-dispatcher` | dispatch | `task_dispatcher.md` | department ルーティング |
| `asana-buddy` | execute | `asana_buddy.md` | Handoff → Asana CRUD |
| `agent-creater` | meta | **なし** | 新規 slug 生成メタスキル |

---

## 企画（planning）

| slug | slot | persona | 委譲元 | persona が効く場面 |
|------|------|---------|--------|-------------------|
| `planning-pm` | dept_orchestrate | `planning_pm.md` | dispatch | review 省略しない |
| `issue-story-planner` | dept_work | `issue_story_planner.md` | planning-pm | 配賦順・測定可能な done_when |
| `plan-reviewer` | dept_review | `plan_reviewer.md` | planning-pm | リスク・配賦漏れ |

---

## UX（v2）

| slug | slot | persona | 委譲元 | persona が効く場面 |
|------|------|---------|--------|-------------------|
| `ux-pm` | dept_orchestrate | `ux_pm.md` | dispatch | 自分で Figma を作らない |
| `ux-designer` | dept_work | `ux_designer.md` | ux-pm | ゴール逆算 · 複数案 · ヒューリスティクス評価 |
| `design-system-owner` | dept_work | `design_system_owner.md` | ux-pm | トークン一貫性 |
| `ux-reviewer` | dept_review | `ux_reviewer.md` | ux-pm / product-manager | 魅力批評・実装一致 |

---

## 開発（v3）

| slug | slot | persona | 委譲元 | persona が効く場面 |
|------|------|---------|--------|-------------------|
| `product-manager` | dept_orchestrate | `product_manager.md` | dispatch | worker 成果物を代行しない |
| `requirements-writer` | dept_work | `requirements_writer.md` | product-manager | 測定可能・as-built |
| `document-author` | dept_work | `document_author.md` | workflow-orchestrator / product-manager | 読者向け説明文書・図表最小十分 |
| `tech-designer` | dept_work | `tech_designer.md` | product-manager | UX/Figma を設計に織り込む |
| `developer` | dept_work | `developer.md` | product-manager | 仕様忠実・最小差分 |
| `dev-reviewer` | dept_review | `dev_reviewer.md` | product-manager | 厳格だが建設的 |
| `qa-verifier` | dept_review | `qa_verifier.md` | product-manager | 独立検証 |

---

## 分析（v2）

| slug | slot | persona | 委譲元 | persona が効く場面 |
|------|------|---------|--------|-------------------|
| `analytics-pm` | dept_orchestrate | `analytics_pm.md` | dispatch | gate 前に ml-engineer を出さない |
| `analytics-requirements-writer` | dept_work | `analytics_requirements_writer.md` | analytics-pm | 測定可能・引き継ぎ可能 |
| `data-architect` | dept_work | `data_architect.md` | analytics-pm | SLA 4 項目必須 |
| `data-engineer` | dept_work | `data_engineer.md` | analytics-pm | 再現性・監査ログ |
| `data-steward` | dept_work | `data_steward.md` | analytics-pm | メタデータ一貫性 |
| `data-analyst` | dept_work | `data_analyst.md` | analytics-pm | 仮説駆動インサイト |
| `data-scientist` | dept_work | `data_scientist.md` | analytics-pm | 評価指標・バイアス |
| `ml-engineer` | dept_work | `ml_engineer.md` | analytics-pm（gate 後） | API 契約の安定 |
| `analysis-reviewer` | dept_review | `analysis_reviewer.md` | analytics-pm | SLA 欠落は failed |

---

## 組織改善（governance）· 監査（audit）

| slug | チーム | slot | persona |
|------|--------|------|---------|
| `governance-pm` | governance | dept_orchestrate | `governance_pm.md` |
| `ssot-implementer` | governance | dept_work | `ssot_implementer.md` |
| `governance-reviewer` | governance | dept_review | `governance_reviewer.md` |
| `audit-pm` | audit | dept_orchestrate | `audit_pm.md` |
| `consistency-auditor` | audit | dept_work | `consistency_auditor.md` |
| `audit-reviewer` | audit | dept_review | `audit_reviewer.md` |

---

## 関連

- [`skill-persona-principles.md`](../design/skill-persona-principles.md)
- [`skills-inventory.md`](skills-inventory.md)
