# reviewer SKILL

> **Deprecated（development-delivery v2）:** [`dev-reviewer`](../dev-reviewer/SKILL.md) と [`qa-verifier`](../qa-verifier/SKILL.md) を使用。registry では `enabled: false`。

**独立スキル:** PM / doc-writer / developer から委譲された **チーム内レビュー・動作検証**。

## review_kind

| review_kind | 入力 | 出力スキーマ |
|-------------|------|--------------|
| `requirements` | 要件定義書 | DocReviewResult |
| `detailed_spec` | 詳細仕様（単独レビュー時） | DocReviewResult |
| `code` | コード変更 | CodeReviewResult |
| `verification` | 実装済み成果 | VerificationResult |
| `mismatch` | 要件定義 + 詳細仕様 | MismatchReviewResult |

## MismatchReviewResult

- `fix_target: document` → doc-writer が仕様修正
- `fix_target: code` → product-manager が developer へ修正依頼（doc-writer 業務完了）

`status: passed*` のとき **署名コメント**（`comment_task.py --agent reviewer`）を投稿して PM へ提出。PM は **`comment_task.py` → `complete_task.py -y` → `DeptWorkComplete`** の順で子タスクを閉じる（[`docs/design/dept-work-io.md`](../../../docs/design/dept-work-io.md)）。

## やらないこと

- 企画 Handoff の plan-reviewer 代替
- 実装・文書の主作成

## 起動例

```
reviewer: review_kind=mismatch で要件定義と詳細仕様の整合を確認し、MismatchReviewResult を返してください。
```
