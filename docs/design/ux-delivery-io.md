# UX チーム delivery I/O

workflow: [`workflows/ux-delivery.yaml`](../../workflows/ux-delivery.yaml) v1 · 組織: [`department-model.md`](department-model.md)

## 組織

| 項目 | 値 |
|------|-----|
| department id | `ux` |
| ラベル | UX チーム |
| PM ハブ | ux-pm |
| スコープ | Asana 子タスク 1 件 = workflow インスタンス 1 本 |
| PM 委譲 | [`ux-pm-assignment.md`](ux-pm-assignment.md) |

### メンバー

| slug | slot | 役割 |
|------|------|------|
| ux-pm | dept_orchestrate | 進行・**タスク分解・アサイン**・artifact 公開・完了 |
| ux-designer | dept_work | 体験設計・Design System・画面仕様 |
| ux-reviewer | dept_review | 体験仕様レビュー・**実装一致レビュー**（development `full-ui` から委譲可） |

---

## チーム間 I/O（公式）

### 入力

| 来源 | 形式 |
|------|------|
| task-dispatcher | `DispatchRequest`（`department: ux`） |
| Asana | 子タスク **notes**（背景・概要・完了条件） |
| Asana（任意） | 親エピック notes |
| 他チーム（任意） | notes の `## 依存（読み取り専用）` — 分析データ契約等 |

**読まないもの:** Handoff JSON、PlanReviewResult

### 出力

| 形式 | 説明 |
|------|------|
| `DeptWorkComplete` | `department: ux`, `status`, `summary`, **`artifacts[]`** |
| Asana | `comment_task.py` → `complete_task.py -y` |
| チーム内成果物 | 下表 |

### 下流（開発チーム）向け公開

Web 画面を持つ development 子（`profile: full-ui`）は、**UX 子完了後**に notes へ以下を転記してから着手する。

```markdown
## 依存（読み取り専用）

| 種別 | 参照 | バージョン | 提供チーム |
|------|------|------------|------------|
| UX 仕様 | `output/ux/specs/<task_gid>-ux-spec.md` | v1.0 | ux |
| Design System | `output/ux/design-system/<task_gid>-design-system.md` | v1.0 | ux |
| Figma（任意） | https://… | — | ux |
```

**利用条件:** 読み取りのみ。UX 変更は **UX チームの子タスク**で依頼する。

### 下流への転記手順（ux-pm → product-manager）

| 順 | 担当 | 操作 |
|----|------|------|
| 1 | **ux-pm** | 全サブ完了後、`DeptWorkComplete.artifacts[]` に `output/ux/...` パスを記載。親 UX 子を complete。 |
| 2 | **product-manager** | full-ui development 子の intake 時、notes に上表 `## 依存` を **`update_task_notes.py --preserve-body`** で追記。 |
| 3 | **product-manager** | 未転記・UX 子未完了なら着手不可（[`development-pm-assignment.md`](development-pm-assignment.md)）。 |

ux-pm は development PM の代わりに依存節を書かない（チーム間 I/O は consume 側 PM の責務）。

---

UX チーム PM 委譲（**タスク分解・アサイン必須**）: [`ux-pm-assignment.md`](ux-pm-assignment.md)

---

## チーム内 workflow

```
ux-pm（intake・タスク洗い出し）
  → pm_assign_subtasks（サブタスク作成 + 各 担当:）
  → ux-designer（体験設計書 / Design System — サブ単位）
  → ux-reviewer（ux_spec — サブ単位）
  → ux-pm（artifacts 確定・親 complete）
```

## 必須ゲート

| ゲート | 担当 | failed 時の修正担当 |
|--------|------|---------------------|
| `ux_review_passed` | ux-reviewer | ux-designer |

`failed` 時: ux-pm が修正サブ → 再 review サブを新規追加（[`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)）。

## 体験設計書の最低項目

| 項目 | 説明 |
|------|------|
| ユーザーフロー | 主要タスクの操作系列 |
| 情報設計（IA） | 画面一覧・ナビゲーション |
| 画面仕様 | 各画面の要素・状態・エラー |
| Design System | トークン・タイポ・Spacing・コンポーネント |
| a11y | 目標 WCAG レベル・キーボード・コントラスト方針 |

## 必須運用

| ルール | 内容 |
|--------|------|
| **PM アサイン** | 必須サブタスク分解 + notes `担当:`（[`ux-pm-assignment.md`](ux-pm-assignment.md)） |
| Epic 内順序 | **UI 系 development 子より先**に UX 子を完了 |
| artifact ID | `artifacts[]` に安定パスを含める |
| 実装一致 | development `full-ui` 完了前に ux-reviewer（`ux_implementation`）が passed* |

---

## チーム内成果物

| 種別 | 推奨パス |
|------|----------|
| 体験設計書 | `output/ux/specs/<task_gid>-ux-spec.md` |
| Design System | `output/ux/design-system/<task_gid>-design-system.md` |
| レビュー | `output/ux/reviews/` |

---

## やらないこと

- Handoff 新規作成（→ 企画チーム）
- 実装・API 設計（→ 開発チーム）
- 他チーム成果物の直接編集
- dispatch（→ 統括グループ）

---

## 関連

- PM: [`skills/ux/ux-pm/SKILL.md`](../../skills/ux/ux-pm/SKILL.md)
- 開発 consume: [`development-delivery-io.md`](development-delivery-io.md)（`profile: full-ui`）
- チーム間: [`dept-work-io.md`](dept-work-io.md)
