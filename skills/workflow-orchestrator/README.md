# workflow-orchestrator

[`workflows/default.yaml`](../../workflows/default.yaml) と [`workflows/agent-registry.yaml`](../../workflows/agent-registry.yaml) を参照し、現段階・ゲート・**次に呼ぶスキル**を案内する薄いルータです。

**作成経路:** [`agent-creater`](../agent-creater/SKILL.md) 契約で整備。

## 使い方

1. 改訂済み Handoff と（あれば）`PlanReviewResult` を渡す
2. オーケストレーターが `review_passed` / `handoff_approved` を確認
3. 次スキル（通常 `asana-buddy`）と起動プロンプト例を返す

新規エージェントが必要な場合は **agent-creater** へ誘導（本スキルは雛形を生成しない）。

詳細: [`SKILL.md`](SKILL.md)、I/O: [`docs/design/workflow-io-contract.md`](../../docs/design/workflow-io-contract.md)

## 未登録スキル

registry に無い slug を workflow が参照した場合、エラー内容と registry 更新手順を返す（実行はしない）。
