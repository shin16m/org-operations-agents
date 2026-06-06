# 企画チーム delivery I/O

workflow: [`workflows/planning-delivery.yaml`](../../workflows/planning-delivery.yaml) · 組織: [`department-model.md`](department-model.md)

## 組織

| 項目 | 値 |
|------|-----|
| department id | `planning` |
| ラベル | 企画チーム |
| PM ハブ | planning-pm |
| ミッション | 企画成果を **Asana タスク群**に落とし込む（他チームの公式入力源） |

---

## チーム間 I/O（公式）

### 入力

| 来源 | 形式 |
|------|------|
| task-dispatcher | `DispatchRequest`（`department: planning`） |
| Asana | 企画子タスク notes + 親エピック notes（生課題） |
| 統括グループ（L1） | bootstrap 用 Handoff → `handoff_to_asana.py` で **Asana 反映済み**の企画子（planning-pm は JSON ではなく **notes** を読む） |

### 出力（他チームが受け取るもの）

| 形式 | 他チームから見た役割 |
|------|------------------|
| **Asana 親エピック + execution 系子タスク** | 各子の **notes**（背景・概要・完了条件・`チーム:`） |
| `DeptWorkComplete` | 統括グループへの企画子完了報告 |

**チーム間 I/O として渡さないもの**

- `AsanaBuddyHandoff` JSON ファイル — **企画チーム内のみ**（planner → reviewer → asana-buddy の入力）
- `PlanReviewResult` — **企画チーム内のみ**

他チーム（開発・分析）は Handoff JSON を読まない。Asana notes が唯一の公式入力。

**チーム横断の依存:** execution 系子の `background` / `summary` / `done_when` に、上流成果物への参照を書く。Asana 反映後は notes の **`## 依存（読み取り専用）`** として読める（[`department-model.md`](department-model.md#成果物共有読み取り専用)）。issue-story-planner は分析→開発など **子タスク間依存**があるとき Handoff subtask に明記する。

---

## チーム内 workflow 概要

[`workflows/planning-delivery.yaml`](../../workflows/planning-delivery.yaml)

```
planning-pm（intake）
  → issue-story-planner（Handoff JSON）
  → plan-reviewer（PlanReviewResult・必須）
  → planning-pm（gate — 直接チャットは同一セッション可 · Asana ドリブンは人間承認）
  → asana-buddy（sync）
  → planning-pm（complete）
```

---

## チーム内 I/O

| 成果物 | パス | 担当 |
|--------|------|------|
| bootstrap Handoff | `output/planning/handoff/bootstrap.*.json` | 統括グループ（intake）→ asana-buddy |
| 本番 Handoff | `output/planning/handoff/*.json` | issue-story-planner |
| PlanReviewResult | `output/planning/plan-review/*.json` | plan-reviewer |

### チーム内ゲート

| ゲート | 条件 |
|--------|------|
| `review_passed` | `PlanReviewResult.status` が `passed` / `passed_with_notes` |
| `handoff_approved` | planning-pm（pm_gate）。**デフォルト:** 要約提示後同一セッションで可。**opt-in:** 【承認】サブ complete 必須（[`planning-gate-vs-pm-review-gate.md`](planning-gate-vs-pm-review-gate.md)） |

---

## やらないこと

- execution 系子の要件定義・実装（→ 開発チーム / 分析チーム）
- ディスパッチ（→ task-dispatcher）
- 他チーム workflow の変更

---

## bootstrap（統括グループ連携）

intake 時: 親 + `department: planning` 子 1 件。`handoff_to_asana.py` は **`--require-review-result` なし**。

## 本番投入（asana_execute）

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\handoff_to_asana.py `
  --handoff .\output\planning\handoff\<theme>.json `
  --require-review-result .\output\planning\plan-review\<theme>.json `
  -y --if-not-exists
```

**bootstrap 後（同一 epic.title が既に存在）:** `--if-not-exists` は **skip せず sync** する。

- 親 `notes` を Handoff の `epic.notes_markdown` で更新
- 子は **【n/m】** タイトルで対応付け → 更新
- bootstrap 企画子（【n/m】なし・`チーム: planning` のみ）→ Handoff 先頭の planning 子と **fuzzy マッチ**（1 件のみ）
- 不足分は **新規 create**

明示的な親 GID 指定: `--parent <PARENT_GID>`（`--if-not-exists` なしでも sync モード）。

---

## 関連

- [`dept-work-io.md`](dept-work-io.md) · [`handoff-v12-department.md`](handoff-v12-department.md)
- PM: [`skills/planning/planning-pm/SKILL.md`](../../skills/planning/planning-pm/SKILL.md)
