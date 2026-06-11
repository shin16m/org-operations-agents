# 本番 SLA テンプレ

| 版 | 1.0 |
| 日付 | 2026-06-11 |
| 適用 | **completion_target: 100%** |
| 親 SSOT | [`delivery-completion-standard.md`](delivery-completion-standard.md) |

## 既定 SLA（org-operations-agents 系 · 参考値）

| 指標 | 既定 | 検証方法 |
|------|------|----------|
| **uptime** | 99.5% / 月（staging 相当） | ヘルスチェック 5 分間隔 · 30 日ロールアップ |
| **p95 応答** | API < 500ms · 静的 UI < 200ms | `/metrics` または load test 1 回記録 |
| **データ鮮度** | `meta.generated_at` が UI 表示 · 24h 以内 | qa evidence · 画面キャプチャ |

## 要件定義への追記（§SLA）

```markdown
## SLA（100% 到達時）

| 指標 | 目標 | 検証 |
|------|------|------|
| uptime | （数値） | （コマンド / ダッシュボード） |
| p95 応答 | （数値） | （コマンド） |
| データ鮮度 | （数値） | （AC 参照） |
```

## 連携

| 経路 | 参照 |
|------|------|
| full-ui + 分析 consume | [`development-delivery-io.md`](development-delivery-io.md) · bundle `generated_at` |
| insights ダッシュボード | 分析 PM `## 依存` 表の API URL + 鮮度 AC |
| 本番デプロイ | [`production-deploy-ac-template.md`](production-deploy-ac-template.md) DEP-3 監視 |

## Epic 完了サマリ

[`epic-completion-summary-template.md`](epic-completion-summary-template.md) の `COMPLETION_LEVEL=100%` 時に SLA 達成行を必須とする。
