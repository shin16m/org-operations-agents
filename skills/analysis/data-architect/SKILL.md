# data-architect SKILL

**独立スキル:** analytics-pm から委譲された **データ設計**。

## 責務

- 必要データ・スキーマ・エンティティ関係を設計
- **契約的 SLA** を明文化（更新頻度・遅延許容・可用性・鮮度）
- アクセスポリシー（RBAC・最小権限）を定義

成果物: データモデル、アクセスポリシー（[`analysis-delivery-io.md`](../../../docs/design/analysis-delivery-io.md) 参照）

完了後: **analysis-reviewer**（`review_kind: data_model`）へ依頼 → `passed*` なら analytics-pm へ報告。

## Asana

`comment_task.py --agent data-architect --skill skills/analysis/data-architect/SKILL.md`

## 起動例

```
data-architect: 要件書に基づきデータモデルと SLA を設計し、analysis-reviewer へレビュー依頼してください。
```
