# 開発チーム delivery I/O

workflow: [`workflows/development-delivery.yaml`](../../workflows/development-delivery.yaml) v2 · 組織: [`department-model.md`](department-model.md)

## 組織

| 項目 | 値 |
|------|-----|
| department id | `development` |
| ラベル | 開発チーム |
| PM ハブ | product-manager |
| スコープ | Asana 子タスク 1 件 = workflow インスタンス 1 本 |
| PM 委譲 | [`development-pm-assignment.md`](development-pm-assignment.md) |

### メンバー（v2）

| slug | slot | 役割 |
|------|------|------|
| product-manager | dept_orchestrate | 進行・profile・委譲・完了 |
| requirements-writer | dept_work | 要件定義・事後詳細仕様 |
| tech-designer | dept_work | 技術設計（実装前） |
| developer | dept_work | 実装 |
| dev-reviewer | dept_review | 要件・設計・コード・mismatch レビュー |
| qa-verifier | dept_review | 動作検証 |

**Deprecated:** `doc-writer` / `reviewer`（v1）— registry `enabled: false`

---

## チーム間 I/O（公式）

### 入力

| 来源 | 形式 | 必須フィールド |
|------|------|----------------|
| task-dispatcher | `DispatchRequest` | `task_gid`, `department: development` |
| Asana | 子タスク **notes** | 背景・概要・完了条件（`## 背景` 等） |
| Asana（任意） | 親エピック notes | エピック全体の文脈 |

**読まないもの:** Handoff JSON、PlanReviewResult、企画チーム `output/planning/`（workflow 入力として）

**他チーム artifact の利用:** [`department-model.md`](department-model.md#成果物共有読み取り専用) — notes の `## 依存（読み取り専用）` に従う **読み取り専用 consume** は可。`output/analysis/` 等の直接探索・編集は不可。

### 出力

| 形式 | 説明 |
|------|------|
| `DeptWorkComplete` | `department: development`, `status`, `summary`, `artifacts[]` |
| Asana | `comment_task.py` → `complete_task.py -y` |
| チーム内成果物 | 下表 |

---

## チーム内 workflow（v2）

```
product-manager（intake・profile）
  → requirements-writer（要件）
  → dev-reviewer（requirements）
  → tech-designer（設計）          ← lite/doc-only で skip
  → dev-reviewer（design）
  → developer（実装）              ← doc-only で skip
  → dev-reviewer（code）
  → qa-verifier（verification）
  → requirements-writer（事後仕様）
  → dev-reviewer（mismatch）
  → product-manager（complete）
```

### delivery profile

| profile | 用途 |
|---------|------|
| `full` | 新機能・API・複数モジュール |
| `lite` | 小変更・バグ修正（設計 skip） |
| `doc-only` | 仕様整備のみ |

notes 先頭 `profile: lite` 等。詳細: [`development-pm-assignment.md`](development-pm-assignment.md)

## 必須ゲート

| ゲート | 担当 | 差し戻し |
|--------|------|----------|
| `requirements_review_passed` | dev-reviewer | requirements-writer |
| `design_review_passed` | dev-reviewer | tech-designer |
| `code_review_passed` | dev-reviewer | developer |
| `verification_passed` | qa-verifier | developer |
| `mismatch_resolved` | dev-reviewer | spec → requirements-writer / code → developer |

## 必須運用

| ルール | 内容 |
|--------|------|
| 入力源 | 子 notes のみ |
| 成果物命名 | `<task_gid>` をファイル名に含める |
| Asana | 委譲ロール `comment_task` → PM `complete_task` |
| 検証独立性 | 動作検証は **qa-verifier のみ**（developer / dev-reviewer は不可） |
| 上流 artifact | `## 依存（読み取り専用）` の表どおり利用。不足時は PM が上流へ差し戻し（直接編集しない） |

---

## チーム内 I/O

| フェーズ | 担当 | 成果物 | 推奨パス |
|----------|------|--------|----------|
| 要件定義 | requirements-writer | 要件定義書 | `output/development/requirements/<task_gid>-requirements.md` |
| 技術設計 | tech-designer | 設計書 | `output/development/design/<task_gid>-design.md` |
| 実装 | developer | コード | 別リポジトリまたは本リポジトリ |
| 事後仕様 | requirements-writer | 詳細仕様書 | `output/development/specs/<task_gid>-spec.md` |
| レビュー | dev-reviewer / qa-verifier | 各 Result JSON | `output/development/reviews/` |

チーム内レビュー契約: [`dept-work-io.md`](dept-work-io.md)

---

## やらないこと

- Handoff 新規作成（→ 企画チーム）
- ディスパッチ（→ 統括グループ）
- 他チーム成果物の直接編集
- 新規 skill フォルダ（→ agent-creater）

---

## 関連

- PM: [`skills/development/product-manager/SKILL.md`](../../skills/development/product-manager/SKILL.md)
- チーム間: [`dept-work-io.md`](dept-work-io.md)
