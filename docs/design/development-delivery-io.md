# 開発チーム delivery I/O

workflow: [`workflows/development-delivery.yaml`](../../workflows/development-delivery.yaml) v3 · 組織: [`department-model.md`](department-model.md)

## 組織

| 項目 | 値 |
|------|-----|
| department id | `development` |
| ラベル | 開発チーム |
| PM ハブ | product-manager |
| スコープ | Asana 子タスク 1 件 = workflow インスタンス 1 本 |
| PM 委譲 | [`development-pm-assignment.md`](development-pm-assignment.md) |
| dispatch 起動 | [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md#development) |

### メンバー（v3）

| slug | slot | 役割 |
|------|------|------|
| product-manager | dept_orchestrate | 進行・profile・委譲・完了 |
| requirements-writer | dept_work | 要件定義・事後詳細仕様 |
| tech-designer | dept_work | 技術設計（実装前） |
| developer | dept_work | 実装 |
| dev-reviewer | dept_review | 要件・設計・コード・mismatch レビュー |
| qa-verifier | dept_review | 動作検証 |
| ux-reviewer | dept_review | **full-ui** 時の実装一致 review（UX チーム所属・開発 PM から委譲） |

---

## チーム間 I/O（公式）

### 入力

| 来源 | 形式 | 必須フィールド |
|------|------|----------------|
| task-dispatcher | `DispatchRequest` | `task_gid`, `department: development` |
| Asana | 子タスク **notes** | 背景・概要・完了条件（`## 背景` 等） |
| Asana（任意） | 親エピック notes | エピック全体の文脈 |
| UX チーム（full-ui） | notes **`## 依存（読み取り専用）`** | UX 仕様・Design System への参照 |

**読まないもの:** Handoff JSON、PlanReviewResult、企画チーム `output/planning/`（workflow 入力として）

**他チーム artifact:** [`department-model.md`](department-model.md#成果物共有読み取り専用) — UX・分析 artifact は notes 経由で read-only consume。

### 出力

| 形式 | 説明 |
|------|------|
| `DeptWorkComplete` | `department: development`, `status`, `summary`, `artifacts[]` |
| Asana | `comment_task.py` → `complete_task.py -y` |
| チーム内成果物 | 下表 |

---

## doc-only 経路（サマリ）

```
product-manager → pm_assign（要件 + review + 事後仕様 + mismatch）→ 【レビュー】人間
  → requirements-writer（要件）→ dev-reviewer → requirements-writer（spec）→ dev-reviewer
```

設計・developer・qa-verifier は workflow 上 skip。詳細: [`development-pm-assignment.md`](development-pm-assignment.md) profile 選定ガイド。

## チーム内 workflow（v3）

```
product-manager（intake・profile・サブタスク分解）
  → requirements-writer（要件）              ← 各フェーズは Asana サブタスク
  → dev-reviewer（requirements）
  → tech-designer（設計）          ← lite/doc-only で skip
  → dev-reviewer（design）
  → developer（実装）              ← doc-only で skip
  → dev-reviewer（code）
  → ux-reviewer（ux_implementation）← full-ui のみ
  → qa-verifier（verification）
  → requirements-writer（事後仕様）
  → dev-reviewer（mismatch）
  → product-manager（complete）
```

### delivery profile

| profile | 用途 |
|---------|------|
| `full` | API / BFF / 非 UI |
| **`full-ui`** | Web 画面 — **UX 子完了 + `## 依存` 必須** |
| `lite` | **非 UI** の小変更・バグ修正（設計 skip）。**画面タッチの子では使用禁止** |
| `doc-only` | 仕様整備のみ |

notes 先頭 `profile: full-ui` 等。詳細: [`development-pm-assignment.md`](development-pm-assignment.md)

### full-ui 前提（Epic 内）

1. 同一 Epic の **UX 子タスクが完了**していること
2. notes に `## 依存（読み取り専用）` で UX artifact が記載されていること
3. 未充足時 PM は着手せず、ux-pm または企画経由で差し戻し

---

## 必須ゲート

| ゲート | 担当 | failed 時の修正担当 |
|--------|------|---------------------|
| `requirements_review_passed` | dev-reviewer | requirements-writer |
| `design_review_passed` | dev-reviewer | tech-designer |
| `code_review_passed` | dev-reviewer | developer |
| `ux_implementation_review_passed` | ux-reviewer | developer（full-ui のみ） |
| `verification_passed` | qa-verifier | developer |
| `mismatch_resolved` | dev-reviewer | spec → requirements-writer / code → developer |

`failed` 時: PM が **修正サブタスクを新規追加** → 修正後 **再 review サブを新規追加**。完了タスクの `--undo` 禁止（[`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)）。

## 必須運用

| ルール | 内容 |
|--------|------|
| 入力源 | 子 notes のみ |
| PM アサイン | **フェーズをサブタスク分解**し各 notes に `担当:`（[`development-pm-assignment.md`](development-pm-assignment.md)） |
| 成果物命名 | `<task_gid>` をファイル名に含める |
| Asana md 添付 | requirements / as-built-spec: worker サブ + **対応 dev-reviewer review サブ**へ同一 md（`attach_task_files.py --also-gid` · [`resolve_dev_review_sub.py`](../../tools/resolve_dev_review_sub.py)） |
| Asana | 委譲ロール `comment_task` → PM がサブ `complete_task` → 全サブ完了後に親 complete |
| 検証独立性 | 動作検証は **qa-verifier のみ** |
| UX consume | full-ui は UX artifact を read-only。変更は UX チーム子タスクで |
| tech-designer | full-ui 時は UX 仕様を設計書に引用 |

---

## チーム内 I/O

| フェーズ | 担当 | 成果物 | 推奨パス |
|----------|------|--------|----------|
| 要件定義 | requirements-writer | 要件定義書 | `output/development/requirements/<task_gid>-requirements.md` |
| 技術設計 | tech-designer | 設計書 | `output/development/design/<task_gid>-design.md` |
| 実装 | developer | コード | 別リポジトリまたは本リポジトリ |
| 事後仕様 | requirements-writer | 詳細仕様書 | `output/development/specs/<task_gid>-spec.md` |
| Asana 添付 | requirements-writer | 要件 / 仕様 md | worker + review サブ attachment（`attach_task_files.py --also-gid`） |
| レビュー | dev-reviewer / qa-verifier / ux-reviewer | 各 Result JSON | `output/development/reviews/` · `output/ux/reviews/` |

チーム内レビュー契約: [`dept-work-io.md`](dept-work-io.md)

---

## やらないこと

- Handoff 新規作成（→ 企画チーム）
- 体験設計の主作成（→ UX チーム）
- ディスパッチ（→ 統括グループ）
- 他チーム成果物の直接編集
- 新規 skill フォルダ（→ agent-creater）

---

## 関連

- PM: [`skills/development/product-manager/SKILL.md`](../../skills/development/product-manager/SKILL.md)
- UX 提供側: [`ux-delivery-io.md`](ux-delivery-io.md)
- チーム間: [`dept-work-io.md`](dept-work-io.md)
