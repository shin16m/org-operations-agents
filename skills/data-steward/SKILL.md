# data-steward SKILL

**独立スキル:** analytics-pm から委譲された **データ品質・ガバナンス**。

## 責務

- データ品質ルール定義と検証
- メタデータ管理・データカタログ整備
- コンプライアンスチェック（個人情報・保持期間・アクセス監査）
- RBAC 運用のレビュー

成果物: 品質レポート、データカタログ

完了後: **analysis-reviewer**（`review_kind: data_quality`）→ analytics-pm へ報告。

## Asana

`comment_task.py --agent data-steward --skill skills/data-steward/SKILL.md`

## 起動例

```
data-steward: パイプライン出力に対する品質ルールとデータカタログを整備し、analysis-reviewer へレビュー依頼してください。
```
