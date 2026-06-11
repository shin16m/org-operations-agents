# エッジケース AC チェックリスト — 100% 到達時

| 版 | 1.0 |
| 日付 | 2026-06-11 |
| 適用 | **completion_target: 100%** · profile `full` / `full-ui` |
| 親 SSOT | [`delivery-completion-standard.md`](delivery-completion-standard.md) |

## カテゴリ（100% 時 Must カバレッジ ≥ 80%）

| カテゴリ | 確認内容 | qa / dev-reviewer |
|----------|----------|-------------------|
| **空データ** | 0 件 · null · 空配列で UI/API が破綻しない | evidence または finding |
| **権限なし** | 401/403 時に依頼者向けメッセージ（スタック trace 非露出） | verification |
| **タイムアウト** | 外部依存失敗時の retry / エラー UI | design + qa |
| **入力境界** | 最大長 · 不正形式 · XSS エスケープ（画面タッチ時） | code review |
| **同時操作** | 二重 submit · 競合更新の扱い（該当時） | design または qa |

## 要件への落とし込み

100% Epic では Should AC に最低 **3 カテゴリ**を 1 行ずつ追加する（例: AC-EC-1 空データ · AC-EC-2 403 · AC-EC-3 タイムアウト）。

## dev-reviewer / qa-verifier

- **requirements review**: 100% 宣言時に EC カテゴリ 3 件未満 → `passed_with_notes` または `failed`（Epic スコープによる）
- **verification**: 記載された EC AC 各行について `evidence[]` 必須

## fixture

- [`docs/verification/fixtures/development/edge-case-review-fixture.v1.json`](../verification/fixtures/development/edge-case-review-fixture.v1.json)
