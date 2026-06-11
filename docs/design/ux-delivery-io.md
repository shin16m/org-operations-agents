# UX チーム delivery I/O

workflow: [`workflows/ux-delivery.yaml`](../../workflows/ux-delivery.yaml) v2 · 組織: [`department-model.md`](department-model.md) · 強みの型: [`delivery-strength-pattern.md`](delivery-strength-pattern.md)

## 組織

| 項目 | 値 |
|------|-----|
| department id | `ux` |
| ラベル | UX チーム |
| PM ハブ | ux-pm |
| スコープ | Asana 子タスク 1 件 = workflow インスタンス 1 本 |
| PM 委譲 | [`ux-pm-assignment.md`](ux-pm-assignment.md) |

### メンバー（v2）

| slug | slot | 役割 |
|------|------|------|
| ux-pm | dept_orchestrate | 進行・profile・**タスク分解・アサイン**・artifact 公開・完了 |
| ux-designer | dept_work | **Figma 画面 UI** · 体験設計 companion 文書 |
| design-system-owner | dept_work | **Figma DS**（変数・コンポーネント）· design-system.md · 任意 Code Connect |
| ux-reviewer | dept_review | **design_quality** · **ux_spec** · 実装一致（development `full-ui` から委譲可） |

> **ux-researcher:** v2 では専ロールなし。`flagship` の IA・フロー探索は **ux-designer** が兼担（[`skill-persona-principles.md`](skill-persona-principles.md)）。

---

## delivery profile

| profile | 用途 | スキップする段階 |
|---------|------|------------------|
| **`flagship`** | 新規 Web アプリ · ブランド体験 · 「これいいな」を追求 | なし（複数案必須） |
| **`standard`**（省略時） | 通常の画面追加・改修 | なし |
| **`lite`** | 既存 DS 流用 · 文言・微調整のみ | visual Figma 新規 · design_quality · design-system-owner |

profile 選定: [`ux-pm-assignment.md`](ux-pm-assignment.md) § profile 選定ガイド

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
| `DeptWorkComplete` | `department: ux`, `status`, `summary`, **`artifacts[]`**（md パス **+ Figma URL**） |
| Asana | `comment_task.py` → `complete_task.py -y` |
| チーム内成果物 | 下表 |

### 下流（開発チーム）向け公開

Web 画面を持つ development 子（`profile: full-ui`）は、**UX 子完了後**に notes へ転記してから着手する。

詳細テンプレ: [`cross-team-artifact-bridge.md`](cross-team-artifact-bridge.md)

```markdown
## 依存（読み取り専用）

| 種別 | 参照 | バージョン | 提供チーム |
|------|------|------------|------------|
| UX 仕様 | `output/ux/specs/<task_gid>-ux-spec.md` | v1.0 | ux |
| Figma UI | https://www.figma.com/design/… | v1.0 | ux |
| Design System | `output/ux/design-system/<task_gid>-design-system.md` | v1.0 | ux |
| Figma DS | https://www.figma.com/design/… | v1.0 | ux |
```

**利用条件:** 読み取りのみ。UX 変更は **UX チームの子タスク**で依頼する。

### 下流への転記手順（ux-pm → product-manager）

| 順 | 担当 | 操作 |
|----|------|------|
| 1 | **ux-pm** | 全サブ完了後、`DeptWorkComplete.artifacts[]` に md パスと Figma URL を記載。親 UX 子を complete。 |
| 2 | **product-manager** | full-ui development 子の intake 時、notes に上表 `## 依存` を **`update_task_notes.py --preserve-body`** で追記。 |
| 3 | **product-manager** | 未転記・UX 子未完了なら着手不可（[`development-pm-assignment.md`](development-pm-assignment.md)）。 |

---

## チーム内 workflow（v2）

```
ux-pm（intake・profile・タスク洗い出し）
  → pm_assign_subtasks（サブタスク作成 + 各 担当:）
  → ux-designer（Figma UI + ux-spec.md — flagship は複数案）
  → ux-reviewer（design_quality — lite 除く）
  → design-system-owner（Figma DS + design-system.md — lite 除く）
  → ux-reviewer（ux_spec）
  → ux-pm（artifacts 確定・親 complete）
```

## 必須ゲート

| ゲート | 担当 | review_kind | failed 時の修正担当 |
|--------|------|-------------|---------------------|
| `design_quality_passed` | ux-reviewer | `design_quality` | ux-designer |
| `ux_spec_passed` | ux-reviewer | `ux_spec` | ux-designer / design-system-owner |

`failed` 時: ux-pm が修正サブ → 再 review サブを新規追加（[`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)）。

### design_quality の評価観点

| 観点 | 内容 |
|------|------|
| 魅力 | 「これいいな」と感じるビジュアルか。凡庸なテンプレ感がないか |
| 一貫性 | 画面間・コンポーネント間の統一感 |
| 意図の明確さ | ユーザーが次に何をすべきか視覚的に分かるか |
| DS 準備 | design-system-owner が着手できる粒度か（lite 除く） |

## 体験設計 companion 文書の最低項目

| 項目 | 説明 |
|------|------|
| Figma URL | 各主要画面の node-id リンク |
| ユーザーフロー | 主要タスクの操作系列 |
| 情報設計（IA） | 画面一覧・ナビゲーション |
| 画面仕様 | 各画面の要素・状態・エラー |
| a11y | 目標 WCAG レベル・キーボード・コントラスト方針 |

## 必須運用

| ルール | 内容 |
|--------|------|
| **PM アサイン** | 必須サブタスク分解 + notes `担当:`（[`ux-pm-assignment.md`](ux-pm-assignment.md)） |
| **Figma 必須** | `standard` / `flagship` では Figma UI が成果物。markdown のみは不可 |
| Epic 内順序 | **UI 系 development 子より先**に UX 子を完了 |
| artifact ID | `artifacts[]` に安定パス **と Figma URL** を含める |
| 実装一致 | development `full-ui` 完了前に ux-reviewer（`ux_implementation`）が passed* |

---

## チーム内成果物

| 種別 | 推奨パス |
|------|----------|
| Figma UI | Figma ファイル URL（DeptWorkComplete に記載） |
| 体験設計 companion | `output/ux/specs/<task_gid>-ux-spec.md` |
| Design System 文書 | `output/ux/design-system/<task_gid>-design-system.md` |
| Figma DS | Figma ファイル URL |
| Code Connect（任意） | `output/ux/code-connect/<task_gid>/` |
| レビュー | `output/ux/reviews/` |

---

## 100% polish（M8 · completion_target: 100）

`full-ui` かつ development 側 `completion_target: 100` のとき、ux-reviewer **ux_implementation** で polish ゲート必須。

| 観点 | UX 成果物での確認 |
|------|-------------------|
| a11y | spec にキーボード · コントラスト方針 |
| エラー | 空状態 · API 失敗時の UI 案 |
| polish | Figma にエラー/空状態フレーム |

SSOT: [`delivery-completion-standard.md`](delivery-completion-standard.md) v2 · [`ux-reviewer` SKILL](../../skills/ux/ux-reviewer/SKILL.md)

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
- チーム間 bridge: [`cross-team-artifact-bridge.md`](cross-team-artifact-bridge.md)
- チーム間: [`dept-work-io.md`](dept-work-io.md)
