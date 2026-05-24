# チーム取り決め — 索引

各チームの**ミッション・I/O・ゲート・やらないこと**を一覧し、詳細文書へ誘導する。

| レイヤー | 文書 | 内容 |
|----------|------|------|
| 組織全体 | [`department-model.md`](department-model.md) | チーム vs 統括グループ、チーム間 I/O 原則 |
| チーム間共通 | [`dept-work-io.md`](dept-work-io.md) | `DispatchRequest` / `DeptWorkComplete` / Asana 署名 / レビュー Result |
| レビュー NG | [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md) | PM へ提出 · OK 進行 · NG は修正サブ追加（`--undo` 禁止） |
| 成果物ポリシー | [`artifact-policy.md`](artifact-policy.md) | テンプレ vs `output/` 実行時 |
| チーム別 | `*-delivery-io.md` | チーム内 workflow・成果物・ゲート・禁止事項 |
| workflow 定義 | `workflows/*-delivery.yaml` | 段階・agent・gate（機械可読） |
| 登録 | [`workflows/organizations.yaml`](../../workflows/organizations.yaml) | id → workflow / PM / 成果物ルート |

---

## 六チーム比較

| 項目 | 企画 | UX | 開発 | 分析 | 組織改善 | 監査 |
|------|------|-----|------|------|----------|------|
| id | `planning` | `ux` | `development` | `analysis` | `governance` | `audit` |
| PM | planning-pm | ux-pm | product-manager | analytics-pm | governance-pm | audit-pm |
| ミッション | Handoff → gate → Asana | UX 設計 → artifact | 製品要件→実装 | データ→本番ゲート | **org-meta SSOT 実装** | 整合性検証 |
| workflow | planning-delivery | ux-delivery | development-delivery | analysis-delivery | governance-delivery | audit-delivery |
| 成果物 | `output/planning/` | `output/ux/` | `output/development/` | `output/analysis/` | `output/governance/` | `output/audit/` |

### チーム間 I/O（全チーム共通）

| 方向 | 形式 |
|------|------|
| 統括グループ → チーム | `DispatchRequest` + Asana 子 **notes**（`チーム:` / 背景・概要・完了条件） |
| チーム → 統括グループ | `DeptWorkComplete` + `comment_task` + `complete_task` |

**禁止（workflow 入力として）:** Handoff JSON・PlanReviewResult・他チーム `output/` の**無契約な直接探索**。

**許可（成果物共有）:** 他チーム artifact の **読み取り専用利用** — notes の `## 依存（読み取り専用）` 経由（[`department-model.md`](department-model.md)「成果物共有」）。

企画チームのみ Handoff / PlanReview を**チーム内**で使用し、他チームへは **Asana notes** で渡す。

### Asana notes ヘッダ（推奨）

```markdown
チーム: development   # planning | ux | development | analysis | audit
profile: full-ui     # 開発のみ（full-ui / full / lite / doc-only）
担当: developer
状態: assigned        # assigned | in_progress | review | done
```

legacy `課:` 行も読取可。新規投入は `チーム:` を使う（[`handoff-v12-department.md`](handoff-v12-department.md)）。

### 成果物共有（チーム横断・読み取り専用）

分析モデル・UX 仕様等を下流が利用する場合: 上流 `DeptWorkComplete.artifacts[]` → notes の `## 依存（読み取り専用）` → 下流が consume。

**Web アプリ Epic（推奨順）:** planning → **ux**（blocking）→ development（`full-ui`）／ analysis（任意）→ **audit**（組織変更時・最後）

---

## 組織改善チーム

**単位:** 子タスク 1 件 = `governance-delivery` 1 インスタンス。**org-meta 変更。audit の直前。**

| 区分 | 取り決め |
|------|----------|
| 入力 | 親 epic notes · Handoff スコープ |
| PM 必須 | **ssot-implementer → governance-reviewer**（[`governance-pm-assignment.md`](governance-pm-assignment.md)） |
| ミッション | registry · skills · workflow · docs/tools の SSOT 変更 |
| やらないこと | Handoff 設計（→ 企画）、製品コード（→ development）、監査（→ audit） |

→ [`governance-delivery-io.md`](governance-delivery-io.md) · [`org-improvement-workflow.md`](org-improvement-workflow.md)

---

## 監査チーム

**単位:** 子タスク 1 件 = `audit-delivery` 1 インスタンス。**組織変更エピックでは他 execution 子の後・親 complete 直前。**

| 区分 | 取り決め |
|------|----------|
| 入力 | 子 notes（監査対象・変更概要・done_when） |
| PM 必須 | **auditor → reviewer** の 2 サブを `pm_assign_subtasks`（[`audit-pm-assignment.md`](audit-pm-assignment.md)） |
| チーム内フロー | 機械検証 → audit-reviewer（org_governance） |
| 必須ゲート | `audit_review_passed` |
| 二重防御 | CI（毎 PR）+ L3 監査（本 workflow） |
| やらないこと | registry 修正実装、Handoff 作成、dispatch |

→ 詳細: [`audit-delivery-io.md`](audit-delivery-io.md) · PM 委譲: [`audit-pm-assignment.md`](audit-pm-assignment.md)

---

## 企画チーム

**他チームへの公式出力:** Asana 親エピック + execution 系子タスク（各 notes に `チーム: ux|development|analysis`）。

| 区分 | 取り決め |
|------|----------|
| 入力 | `DispatchRequest`、企画子 notes、親 notes（bootstrap は統括が Asana 反映済み） |
| チーム内成果物 | `output/planning/handoff/*.json`、`output/planning/plan-review/*.json` |
| 必須ゲート | `review_passed`（plan-reviewer）→ `handoff_approved`（planning-pm・**人間**） |
| bootstrap | review **なし**で親 + 企画子 1 件 |
| 本番 sync | `--require-review-result` + `--if-not-exists`（既存親は sync） |
| PM 完了 | comment → complete → `DeptWorkComplete` |
| やらないこと | execution 系の実装・要件定義、dispatch |

→ 詳細: [`planning-delivery-io.md`](planning-delivery-io.md)

---

## UX チーム

**単位:** 子タスク 1 件 = `ux-delivery` 1 インスタンス。**Web アプリ Epic では UI 系 development 子より先に完了。**

| 区分 | 取り決め |
|------|----------|
| 入力 | 子 notes、任意の `## 依存`（分析データ契約等） |
| PM 必須 | **必要タスクをサブタスク化**しメンバーへ `担当:` アサイン（[`ux-pm-assignment.md`](ux-pm-assignment.md)） |
| チーム内フロー | 体験設計 → ux-reviewer（ux_spec）→ artifact 公開 |
| 必須ゲート | `ux_review_passed` |
| PM 委譲 | notes に `担当:`。必要なら nested サブタスク + `pm_assign_subtasks.py` |
| 下流 | development `profile: full-ui` が `## 依存` で consume |
| 横断 review | ux-reviewer（`ux_implementation`）— development PM から委譲 |
| やらないこと | 実装、Handoff 作成、dispatch |

→ 詳細: [`ux-delivery-io.md`](ux-delivery-io.md) · PM 委譲: [`ux-pm-assignment.md`](ux-pm-assignment.md)

---

## 開発チーム

**単位:** 子タスク 1 件 = `development-delivery` v3 1 インスタンス。

| 区分 | 取り決め |
|------|----------|
| 入力 | 子 notes（`profile:` / `担当:` / `## 依存`） |
| PM 必須 | **workflow フェーズをサブタスク化**しメンバーへ `担当:` アサイン（[`development-pm-assignment.md`](development-pm-assignment.md)） |
| チーム内フロー | 要件 → 設計 → 実装 → dev-reviewer → **ux-reviewer（full-ui）** → qa-verifier → 事後仕様 |
| profile | `full` / **`full-ui`** / `lite`（非 UI のみ）/ `doc-only` |
| 必須ゲート | 要件 / 設計 / code / **ux_implementation（full-ui）** / verification / mismatch |
| PM 委譲 | notes に `担当:`。nested サブタスク + `pm_assign_subtasks.py`（`--department development`） |
| やらないこと | 体験設計の主作成、Handoff 作成、dispatch、**ワーカー成果物の PM 代行** |

→ 詳細: [`development-delivery-io.md`](development-delivery-io.md) · dispatch: [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md#development)

---

## 分析チーム

**単位:** 子タスク 1 件 = `analysis-delivery` 1 インスタンス。

| 区分 | 取り決め |
|------|----------|
| 入力 | 子 notes のみ |
| チーム内フロー | 要求 → データ設計（**SLA 必須**）→ ETL → 品質 → 探索 → モデル → **production_gate** → デプロイ → 価値検証 |
| 必須ゲート | 各フェーズ review + **`production_deploy_gate`**（ml-engineer 前） |
| SLA | 更新頻度・遅延許容・可用性・鮮度 — data_model review で未記載は failed |
| PM 必須 | **workflow フェーズをサブタスク化**（[`analytics-pm-assignment.md`](analytics-pm-assignment.md)） |
| PM 委譲 | nested サブタスク + `pm_assign_subtasks.py`（`--department analysis`） |
| 成果物 | `output/analysis/` 配下（パイプライン・モデル実体は別リポジトリ） |
| RBAC / 監査 | data-architect 設計、data-steward 確認、本番データ直接アクセス禁止 |
| やらないこと | Handoff 作成、dispatch、他チーム成果物編集 |

→ 詳細: [`analysis-delivery-io.md`](analysis-delivery-io.md) · PM 委譲: [`analytics-pm-assignment.md`](analytics-pm-assignment.md)

---

## 統括グループ（参考）

dispatch 対象外。チーム内 delivery は持たない。

| コンポーネント | 取り決め |
|----------------|----------|
| workflow-orchestrator | intake → bootstrap Handoff → dispatch 委譲 → エピック完了集約 |
| task-dispatcher | 子 1 件 → `organizations.yaml` でチーム PM へ |
| asana-buddy | Asana CRUD・Handoff sync（企画チーム L3 / bootstrap から呼ばれる） |
| agent-creater | 新規 `skills/<dept>/<slug>/` の**唯一**の生成入口 |

---

## 新チームを足すとき

[`department-model.md`](department-model.md) の **4 点セット** + **[`new-department-checklist.md`](new-department-checklist.md)**（A〜H）。

検証: `python tools/validate_org_registry.py`

1. `organizations.yaml` に 1 行
2. `workflows/<id>-delivery.yaml`
3. `docs/design/<id>-delivery-io.md`（本索引の比較表に追記）
4. `skills/<dept>/<pm-slug>/`

本書（`team-conventions.md`）の比較表と、[`CONTRIBUTING.md`](../../CONTRIBUTING.md) を更新する。

---

## 関連

- 配賦モデル: [`department-model.md`](department-model.md)
- E2E: [`default-workflow.md`](../e2e/default-workflow.md) · [`dispatch-workflow.md`](../e2e/dispatch-workflow.md)
- 検証: [`planning-dept-v3-dryrun.md`](../verification/planning-dept-v3-dryrun.md) · [`ux-delivery-v1-dryrun.md`](../verification/ux-delivery-v1-dryrun.md)
