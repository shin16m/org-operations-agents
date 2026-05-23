# チーム取り決め — 索引

各チームの**ミッション・I/O・ゲート・やらないこと**を一覧し、詳細文書へ誘導する。

| レイヤー | 文書 | 内容 |
|----------|------|------|
| 組織全体 | [`department-model.md`](department-model.md) | チーム vs 統括グループ、チーム間 I/O 原則 |
| チーム間共通 | [`dept-work-io.md`](dept-work-io.md) | `DispatchRequest` / `DeptWorkComplete` / Asana 署名 |
| チーム別 | `*-delivery-io.md` | チーム内 workflow・成果物・ゲート・禁止事項 |
| workflow 定義 | `workflows/*-delivery.yaml` | 段階・agent・gate（機械可読） |
| 登録 | [`workflows/organizations.yaml`](../../workflows/organizations.yaml) | id → workflow / PM / 成果物ルート |

---

## 三チーム比較

| 項目 | 企画チーム | 開発チーム | 分析チーム |
|------|------------|------------|------------|
| id | `planning` | `development` | `analysis` |
| PM ハブ | planning-pm | product-manager | analytics-pm |
| ミッション | Handoff → review → gate → **Asana タスク化**（他チームの入力源） | 要件 → 設計 → 実装 → レビュー/QA → **事後仕様** | 要求 → データ → パイプライン → モデル → **本番ゲート** → 価値検証 |
| workflow | [`planning-delivery`](../../workflows/planning-delivery.yaml) | [`development-delivery`](../../workflows/development-delivery.yaml) | [`analysis-delivery`](../../workflows/analysis-delivery.yaml) |
| 詳細 I/O | [`planning-delivery-io.md`](planning-delivery-io.md) | [`development-delivery-io.md`](development-delivery-io.md) | [`analysis-delivery-io.md`](analysis-delivery-io.md) |
| 成果物ルート | `output/planning/` | `output/development/` | `output/analysis/`（実体は別リポジトリ想定） |

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
チーム: development   # planning | development | analysis
担当: developer       # 任意（分析チーム PM 委譲時は必須 — 下記）
状態: assigned        # assigned | in_progress | review | done
```

legacy `課:` 行も読取可。新規投入は `チーム:` を使う（[`handoff-v12-department.md`](handoff-v12-department.md)）。

### 成果物共有（チーム横断・読み取り専用）

分析モデル・データ等を開発が利用する場合: 上流 `DeptWorkComplete.artifacts[]` → notes の `## 依存（読み取り専用）` → 下流が consume。詳細: [`department-model.md`](department-model.md#成果物共有読み取り専用)。

---

## 企画チーム

**他チームへの公式出力:** Asana 親エピック + execution 系子タスク（各 notes に `チーム: development|analysis`）。

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

## 開発チーム

**単位:** 子タスク 1 件 = `development-delivery` 1 インスタンス。

| 区分 | 取り決め |
|------|----------|
| 入力 | 子 notes（`profile:` / `担当:` 可） |
| チーム内フロー | 要件 → 設計（skip可）→ 実装 → dev-reviewer → qa-verifier → 事後仕様 → mismatch |
| profile | `full` / `lite` / `doc-only` |
| 必須ゲート | 要件 / 設計 / code / verification / mismatch |
| PM 委譲 | [`development-pm-assignment.md`](development-pm-assignment.md) |
| やらないこと | Handoff 作成、dispatch |

→ 詳細: [`development-delivery-io.md`](development-delivery-io.md)

---

## 分析チーム

**単位:** 子タスク 1 件 = `analysis-delivery` 1 インスタンス。

| 区分 | 取り決め |
|------|----------|
| 入力 | 子 notes のみ |
| チーム内フロー | 要求 → データ設計（**SLA 必須**）→ ETL → 品質 → 探索 → モデル → **production_gate** → デプロイ → 価値検証 |
| 必須ゲート | 各フェーズ review + **`production_deploy_gate`**（ml-engineer 前） |
| SLA | 更新頻度・遅延許容・可用性・鮮度 — data_model review で未記載は failed |
| PM 委譲 | notes に `担当:` を書く。必要なら nested サブタスク（[`analytics-pm-assignment.md`](analytics-pm-assignment.md)） |
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

[`department-model.md`](department-model.md) の **4 点セット**:

1. `organizations.yaml` に 1 行
2. `workflows/<id>-delivery.yaml`
3. `docs/design/<id>-delivery-io.md`（本索引の比較表に追記）
4. `skills/<dept>/<dept>-pm/`

本書（`team-conventions.md`）の比較表と、[`CONTRIBUTING.md`](../../CONTRIBUTING.md) を更新する。

---

## 関連

- 配賦モデル: [`org-dispatch-model.md`](org-dispatch-model.md)
- E2E: [`default-workflow.md`](../e2e/default-workflow.md) · [`dispatch-workflow.md`](../e2e/dispatch-workflow.md)
- 検証: [`planning-dept-v3-dryrun.md`](../verification/planning-dept-v3-dryrun.md)
