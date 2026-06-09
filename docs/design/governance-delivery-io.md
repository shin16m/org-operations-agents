# 組織改善チーム delivery I/O

workflow: [`workflows/governance-delivery.yaml`](../../workflows/governance-delivery.yaml) · ロール分担: [`org-improvement-workflow.md`](org-improvement-workflow.md)

## 位置づけ

| 項目 | 内容 |
|------|------|
| department id | `governance` |
| ラベル | 組織改善チーム |
| PM ハブ | governance-pm |
| ミッション | **org-meta / SSOT** 変更の実装（registry · skills · workflow · docs · tools） |

**開発チームとの境界:** 製品コード・API・画面は `development`。本リポジトリの **組織定義・運用 SSOT** は `governance`。

---

## いつ dispatch するか

Handoff execution 子に **`department: governance`** を付ける:

- registry / workflow / validate 変更
- 新 department / スキル追加
- cursor rule · dispatch SSOT · design doc の org-meta 更新

**配賦順:** 企画完了後 — 製品子（ux / development）がある場合はその **後**、**audit の直前**（[`department-model.md`](department-model.md)）。

---

## チーム内 workflow

```
governance-pm（intake · pm_assign）
  → ssot-implementer（SSOT ファイル変更 + 実施記録）
  → governance-reviewer（GovernanceReviewResult）
  → governance-pm（comment → complete → DeptWorkComplete）
```

assign plan 例: [`assign-plan.org-meta-v1.json`](../../skills/governance/examples/assign-plan.org-meta-v1.json)

---

## チーム内 I/O

| 成果物 | パス | 担当 |
|--------|------|------|
| 実施記録（任意） | `output/governance/records/<task_gid>-record.md` | ssot-implementer |
| GovernanceReviewResult | `output/governance/reviews/<task_gid>-governance.review.json` | governance-reviewer |
| MilestoneEffectivenessReport | `output/governance/milestone-reports/<tracker_gid>-readiness.json` | governance-pm（tracker 締め時） |

**マイルストーン tracker:** [`milestone-effectiveness-standard.md`](milestone-effectiveness-standard.md) · `check_milestone_readiness.py` · `epic_milestone_readiness_hook.py`

---

## チーム間 I/O

| 入力 | ソース |
|------|--------|
| 変更仕様 | 親エピック notes · 企画 Handoff（読み取り専用参照） |
| 完了報告 | `DeptWorkComplete` → orchestrator |

| 出力 | 先 |
|------|-----|
| git 変更（SSOT） | リポジトリ本体 |
| findings（修正必要） | audit 子へ引き継ぎ（実装完了後） |

---

## やらないこと（governance-pm）

- Handoff 新規作成（→ 企画）
- validate 実行・監査レポート（→ audit）
- 製品アプリの実装（→ development）

---

## 参照

- [`governance-pm-assignment.md`](governance-pm-assignment.md)
- [`new-department-checklist.md`](new-department-checklist.md)
