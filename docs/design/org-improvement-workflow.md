# 組織改善 workflow — ロール分担 SSOT

| 版 | 1.0 |
| 日付 | 2026-05-24 |
| ソース intake | `1215082835252610` |

## 疑問への回答

| 疑問 | 回答 |
|------|------|
| 組織改善のプランは誰が設計？ | **企画** — `issue-story-planner` が Handoff JSON を設計 · `plan-reviewer` がレビュー |
| 具体アクション（SSOT 変更）は誰が？ | **組織改善チーム（governance）** — `ssot-implementer` が registry/skills/doc を変更 |
| 開発チームの役割は？ | **製品**（要件・設計・コード・QA）。org-meta は **governance** へ移管 |
| 統制は？ | **監査** — `audit-pm` · validate + L3（組織変更エピックの最後） |

## 組織改善エピックの典型フロー

```
intake（workflow-orchestrator）
  → planning: issue-story-planner（Handoff 設計）· plan-reviewer · gate
  → governance: ssot-implementer（SSOT 実装）· governance-reviewer
  → audit: consistency-auditor · audit-reviewer
  → 親 complete
```

## 子タスク命名（推奨）

| department | タイトル例 |
|------------|------------|
| planning | 【1/n・企画】Handoff 作成 |
| governance | 【2/n・governance】組織改善 SSOT 整備 |
| audit | 【3/n・監査】組織整合性監査（L3） |

**避ける:** org-meta 変更を `【n/m・開発】` とだけ表記（製品開発と混同）。

## 製品 Epic との共存

| Epic 種別 | execution 子 |
|-----------|--------------|
| 製品のみ | ux → development / analysis（任意） |
| org-meta のみ | governance → audit |
| 両方 | ux → development → **governance**（org 部分）→ audit |

## 参照

- [`department-model.md`](department-model.md)
- [`governance-delivery-io.md`](governance-delivery-io.md)
- [`workflows/governance-delivery.yaml`](../../workflows/governance-delivery.yaml)
