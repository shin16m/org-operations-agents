# doc-writer SKILL

**独立スキル:** PM から委譲された **文書作成**（要件定義書・詳細仕様書）。

## 責務

| フェーズ | 成果物 | 次 |
|----------|--------|-----|
| 要件定義 | `requirements-doc` | reviewer（`review_kind: requirements`） |
| 詳細仕様 | `detailed-spec` | reviewer（`review_kind: mismatch`） |

レビュー `passed*` 後は **product-manager** へ提出。

## やらないこと

- コード実装（→ developer）
- ディスパッチ・PM 進行（→ task-dispatcher / product-manager）

## 出力

作業完了時:

1. **Asana 署名コメント** — `comment_task.py --agent doc-writer --skill skills/development/doc-writer/SKILL.md`（[`agent-asana-comment-signature.md`](../../../docs/design/agent-asana-comment-signature.md)）
2. 成果物パス + 「reviewer へレビュー依頼」の短いメモ

## 起動例

```
doc-writer: 子タスク 1214877045257081 の要件定義書を作成し、reviewer へレビュー依頼してください。
```
