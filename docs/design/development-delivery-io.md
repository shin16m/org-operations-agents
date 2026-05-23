# 開発チーム delivery I/O

workflow: [`workflows/development-delivery.yaml`](../../workflows/development-delivery.yaml) · 組織: [`department-model.md`](department-model.md)

## 組織

| 項目 | 値 |
|------|-----|
| department id | `development` |
| ラベル | 開発チーム |
| PM ハブ | product-manager |
| スコープ | Asana 子タスク 1 件 = workflow インスタンス 1 本 |

---

## チーム間 I/O（公式）

### 入力

| 来源 | 形式 | 必須フィールド |
|------|------|----------------|
| task-dispatcher | `DispatchRequest` | `task_gid`, `department: development` |
| Asana | 子タスク **notes** | 背景・概要・完了条件（`## 背景` 等） |
| Asana（任意） | 親エピック notes | エピック全体の文脈 |

**読まないもの:** Handoff JSON、PlanReviewResult、企画チーム `output/planning/`（チーム間 I/O として禁止）

### 出力

| 形式 | 説明 |
|------|------|
| `DeptWorkComplete` | `department: development`, `status`, `summary`, `artifacts[]` |
| Asana | `comment_task.py`（署名）→ `complete_task.py -y` |
| チーム内成果物 | 下表「チーム内 I/O」 |

---

## チーム内 I/O

| フェーズ | 担当 | 成果物 | 推奨パス |
|----------|------|--------|----------|
| 要件定義 | doc-writer | 要件定義書 | `output/development/requirements/<task_gid>-requirements.md` |
| 実装 | developer | コード | 別リポジトリまたは本リポジトリ内 |
| 詳細仕様 | doc-writer | 詳細仕様書 | `output/development/specs/<task_gid>-spec.md` |
| レビュー | reviewer | DocReviewResult / CodeReviewResult / VerificationResult / MismatchReviewResult | `output/development/reviews/` |

チーム内レビュー契約: [`dept-work-io.md`](dept-work-io.md)

---

## やらないこと

- Handoff 新規作成（→ 企画チーム）
- ディスパッチ（→ task-dispatcher / 統括グループ）
- 他チーム成果物の直接編集
- 新規 `skills/<organization>/<slug>/` 生成（→ agent-creater）

---

## 関連

- PM スキル: [`skills/development/product-manager/SKILL.md`](../../skills/development/product-manager/SKILL.md)
- チーム間共通: [`dept-work-io.md`](dept-work-io.md)
