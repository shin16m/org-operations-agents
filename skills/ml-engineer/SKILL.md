# ml-engineer SKILL

**独立スキル:** analytics-pm から委譲された **デプロイ・運用**（**production_deploy_gate 通過後のみ**）。

## 責務

- モデルのコンテナ化
- CI/CD パイプライン（デプロイ・ロールバック）
- モニタリング・ドリフト検知
- 再学習パイプライン

成果物: デプロイ済モデル、監視ダッシュボード

**着手条件:** `DeployGateResult` で `quality_approved`・`security_approved`・`sla_compliance` がすべて true。

完了後: **analysis-reviewer**（`review_kind: deploy_verification`）→ analytics-pm へ報告。

## Asana

`comment_task.py --agent ml-engineer --skill skills/ml-engineer/SKILL.md`

## やらないこと

- production_deploy_gate 未通過での本番デプロイ
- モデル試作（→ data-scientist）

## 起動例

```
ml-engineer: production_deploy_gate 通過済みモデルをデプロイし、監視を設定して analysis-reviewer へ検証依頼してください。
```
