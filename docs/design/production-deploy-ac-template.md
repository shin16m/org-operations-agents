# 本番デプロイ AC テンプレ

| 版 | 1.0 |
| 日付 | 2026-06-11 |
| 適用 | profile `full` / `full-ui` · **completion_target: 100%** |
| 親 SSOT | [`delivery-completion-standard.md`](delivery-completion-standard.md) |

## 要件定義書への追記（§本番デプロイ AC）

100% 到達 Epic では [`acceptance-criteria-template.md`](acceptance-criteria-template.md) の AC 表に加え、以下を **Must** で追記する。

| ID | 優先度 | 前提 | 操作 / 入力 | 期待結果 | 検証 |
|----|--------|------|-------------|----------|------|
| DEP-1 | Must | staging または本番相当 env | デプロイ手順 1 本実行 | ヘルスエンドポイント 200 | README / runbook 記載コマンド |
| DEP-2 | Must | デプロイ直後 | ロールバック手順 dryrun | 前バージョンへ復旧可能 | runbook 手順 + 記録 md |
| DEP-3 | Must | 本番相当 | 監視アラート 1 件テスト | 通知到達 | metrics / ログ参照 |
| DEP-4 | Should | データ移行あり | 移行スクリプト dryrun | 件数・checksum 一致 | 移行ログ |

## 記載ルール

| ルール | 内容 |
|--------|------|
| 環境 | `staging` / `production` を明記。secret は vault 参照のみ |
| ロールバック | **手順 1 本** + 所要時間目安 |
| 監視 | ヘルス URL · エラー率 · レイテンシのいずれか 1 つ以上 |
| lite / doc-only | 本節 **省略可**（completion_target 80% 以下） |

## 関連

- SLA: [`production-sla-template.md`](production-sla-template.md)
- 100% 完成度: [`delivery-completion-standard.md`](delivery-completion-standard.md) §100% 必須条件
