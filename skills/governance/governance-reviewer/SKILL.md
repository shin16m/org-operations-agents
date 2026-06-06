# governance-reviewer SKILL

人間向け: [`README.md`](README.md) · persona: [`personas/governance_reviewer.md`](personas/governance_reviewer.md)

**独立スキル:** ssot-implementer 成果の **org-meta レビュー**。

スキーマ: [`schemas/governance-review-result.v1.schema.json`](schemas/governance-review-result.v1.schema.json)

## 着手前（必須）

`fetch_task.py --gid <task_gid> --show-assignee` で **担当が governance-reviewer** であることを確認。

## 責務

1. git diff / 実施記録を epic notes · Handoff と照合
2. `GovernanceReviewResult`（`review_kind: org_meta`）を `output/governance/reviews/<task_gid>-governance.review.json` に保存
3. **comment_task.py** → governance-pm へ報告

## やらないこと

- SSOT 修正実装（failed 時は PM が fix サブ作成）
