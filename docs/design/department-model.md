# 組織モデル — チーム・統括グループ・チーム間 I/O

## 組織の種類

| 種類 | 例 | 役割 |
|------|-----|------|
| **チーム** | 企画チーム / 開発チーム / 分析チーム | 自律した delivery。チーム内 workflow と I/O を自分で決める |
| **統括グループ** | workflow-orchestrator, task-dispatcher, asana-buddy, agent-creater | **配線・メタ**。チーム内業務は持たない。dispatch 対象外 |

スキル配置: チーム → `skills/<department>/` · 統括グループ → `skills/platform/`（パス slug は `platform` のまま。表示名は **統括グループ**）

登録: [`workflows/organizations.yaml`](../../workflows/organizations.yaml)

---

## 原則

1. **チーム内自律** — 段階・役割・レビューは各チームの `*-delivery.yaml` が決める
2. **チーム間は契約のみ** — チームをまたぐ公式 I/O は下表に限定する
3. **Handoff JSON はチーム間 I/O に使わない** — 企画チームの**チーム内**成果物。他チームは読まない
4. **統括グループは配線** — intake / bootstrap / dispatch / Asana CRUD。業務判断はチーム PM へ

---

## チーム間 I/O（公式）

| 方向 | 形式 | 説明 |
|------|------|------|
| 統括グループ → チーム | `DispatchRequest` | `task_gid` + `department` |
| 統括グループ → チーム | **Asana 子タスク + notes** | 背景・概要・完了条件・`チーム:` 行 |
| チーム → 統括グループ | `DeptWorkComplete` | 子 1 件の完了報告 |
| チーム → 統括グループ | Asana `comment_task` + `complete_task` | 署名付き記録と完了同期 |

**チーム間 I/O に含めないもの**

- `AsanaBuddyHandoff` JSON ファイル（企画チーム内部）
- `PlanReviewResult`（企画チーム内部）
- 他チームの `output/<dept>/` を **workflow 入力の代わりに直接探索・編集**すること（下記「成果物共有」参照）

**統括グループ / チーム PM の運用ツール（チーム間 I/O ではない）**

- `sync_handoff_epic.py --handoff` — Handoff の子タイトル【n/m】と Asana を照合し一括完了する **Asana 同期**用。要件の受け渡しには使わない。
- bootstrap 用 Handoff JSON — 統括グループが L1 で企画子 1 件を Asana に作成するための**内部成果物**。他チーム PM は読まず、反映済み notes を読む。

企画チームが他チームへ渡す情報は、**Asana 上の親・子タスクと notes** に落とした時点で公式化する。

---

## 成果物共有（読み取り専用）

チームをまたいで **データ・モデル・API 等を利用する**ことは想定どおり。**禁止するのは編集と、notes を経由しない直接参照**である。

### 2 層モデル

| 層 | 役割 | 例 |
|----|------|-----|
| **公式 I/O** | dispatch の入力契約 | Asana 子 notes（背景・概要・完了条件・`## 依存`） |
| **成果物（artifact）** | 各チームが作った実体 | モデルファイル、推論 API、データカタログ、コード |

下流チーム（例: 開発）は **公式 I/O（notes）に書かれた参照**に従って artifact を **consume（読み取り・呼び出し）** する。上流チーム（例: 分析）の `output/analysis/` を PM が勝手に漁って要件の代わりにしない。

### 許可 / 禁止

| | 許可 | 禁止 |
|--|------|------|
| 他チームが **公開した** API・モデル・データセットの利用 | ○ | |
| notes の `## 依存（読み取り専用）` に書かれた URI・パス・バージョンを参照 | ○ | |
| `DeptWorkComplete.artifacts[]` を PM が notes に転記 | ○ | |
| 他チーム `output/<dept>/` を **探索して** workflow 入力とする | | × |
| 他チーム成果物の **編集・上書き** | | × |
| 他チーム workflow 内コード（パイプライン等）の **直接変更** | | ×（変更は該当チームの子タスクで） |

### 典型フロー（UX → 開発）

```
UX チーム完了
  → DeptWorkComplete（artifacts[] に UX 仕様・Design System）
  → product-manager が development 子 notes に ## 依存 を追記
  → development dispatch（profile: full-ui）
  → tech-designer / developer が UX artifact を read-only consume
  → ux-reviewer（ux_implementation）→ qa-verifier
```

### 典型フロー（分析 → 開発）

```
分析チーム完了
  → DeptWorkComplete（artifacts[] にモデル/API/カタログ）
  → 企画 PM が Handoff sync 時、または開発 PM が notes に ## 依存 を追記
  → 開発チーム dispatch
  → developer は notes の依存契約に従いプロダクト実装（artifact は読み取り専用）
```

### notes 記載例（`## 依存（読み取り専用）`）

企画 Handoff の subtask `summary` / `background`、または PM の `update_task_notes.py` で追記する。

```markdown
## 依存（読み取り専用）

| 種別 | 参照 | バージョン | 提供チーム |
|------|------|------------|------------|
| モデル | `output/analysis/models/<task_gid>/` または推論 API URL | v1.0 | analysis |
| データ | `output/analysis/catalog/<task_gid>.md` | 2026-05-23 | analysis |
| SLA | 日次更新・遅延最大 2h（data-architect 設計書参照） | — | analysis |

**利用条件:** 読み取り・呼び出しのみ。パス・API の変更は分析チームの子タスクで依頼する。
```

### 提供側（分析チーム等）の義務

完了時 `DeptWorkComplete.artifacts[]` に、下流が参照する **安定した識別子**（パス・URL・バージョン）を含める。モデル・API には **スキーマ・SLA・アクセス方針** を成果物またはカタログに残す（[`analysis-delivery-io.md`](analysis-delivery-io.md)）。

### 消費側（開発チーム等）の義務

- workflow 入力は **自分の子 notes**（`## 依存` 含む）
- 技術設計・実装は依存表の契約どおり。不足があれば **product-manager** が上流 PM または企画経由で差し戻し（直接 `output/analysis/` を編集しない）

---

## チームの追加ルール（必須 4 点セット）

新規チーム（例: 運用チーム）を足すとき:

| # | 成果物 | 例 |
|---|--------|-----|
| 1 | [`workflows/organizations.yaml`](../../workflows/organizations.yaml) | `departments[]` に 1 行 |
| 2 | `workflows/<id>-delivery.yaml` | チーム内 workflow |
| 3 | `docs/design/<id>-delivery-io.md` | チーム内 I/O + チーム間 I/O + やらないこと |
| 4 | PM ハブスキル | `skills/<dept>/<dept>-pm/`（`dept_orchestrate`） |

追加: チーム内ワーカー・reviewer を `agent-registry.yaml` に登録。統括グループの変更は通常不要。

---

## 既存チーム一覧

| id | ラベル | workflow | PM ハブ | I/O 文書 |
|----|--------|----------|---------|----------|
| `planning` | 企画チーム | `planning-delivery` | planning-pm | [`planning-delivery-io.md`](planning-delivery-io.md) |
| `development` | 開発チーム | `development-delivery` | product-manager | [`development-delivery-io.md`](development-delivery-io.md) |
| `analysis` | 分析チーム | `analysis-delivery` | analytics-pm | [`analysis-delivery-io.md`](analysis-delivery-io.md) |
| `ux` | UX チーム | `ux-delivery` | ux-pm | [`ux-delivery-io.md`](ux-delivery-io.md) |

チーム間共通契約: [`dept-work-io.md`](dept-work-io.md)（`DispatchRequest` / `DeptWorkComplete`）

**チーム取り決め一覧:** [`team-conventions.md`](team-conventions.md)

---

## 三層レイヤー（参照）

```
統括グループ: intake → bootstrap → dispatch 委譲
       ↓
チーム（L3）: PM ハブ → チーム内 workflow → DeptWorkComplete
       ↓
統括グループ: 次の子 dispatch / エピック完了集約
```

詳細: [`org-dispatch-model.md`](org-dispatch-model.md)
