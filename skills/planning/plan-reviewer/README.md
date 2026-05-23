# plan-reviewer

`issue-story-planner` が出力した **AsanaBuddyHandoff v1.1** の有効性・リスク・抜け漏れをレビューし、改訂案または `PlanReviewResult` を返すスキルです。

**標準 workflow では必須段階**（省略不可）。Asana 投入前に `passed` / `passed_with_notes` が必要です。

**作成経路:** 本リポジトリのエピックに沿い [`agent-creater`](../agent-creater/SKILL.md) の契約で整備（手書き新規フォルダは避ける運用）。

詳細は [`SKILL.md`](SKILL.md)。出力契約は [`docs/design/plan-reviewer-contract.md`](../../../docs/design/plan-reviewer-contract.md)。

## 使い方（Copilot / Cursor）

```
あなたは plan-reviewer スキルです。次の AsanaBuddyHandoff JSON をレビューし、
PlanReviewResult（schema_version "1.0"）を1つの JSON コードブロックで出力してください。
必要なら revised_handoff に改訂版 Handoff v1.1 を含めてください。
```

## 検証

1. 入力 Handoff の `schema_version` が `1.1` であること
2. 出力 `status` が `passed` / `passed_with_notes` / `needs_revision` / `blocked` のいずれか
3. `needs_revision` 時は `revised_handoff` または差し戻し理由が明確
