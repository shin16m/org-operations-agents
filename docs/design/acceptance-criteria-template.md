# 受け入れ基準（AC）テンプレ — 要件定義書 Must 節

| 版 | 1.0 |
| 日付 | 2026-06-08 |
| 適用 | requirements-writer（mode=requirements）· dev-reviewer（requirements） |
| 完成度 SSOT | [`delivery-completion-standard.md`](delivery-completion-standard.md) |

## 要件定義書への貼り付け（§受け入れ基準）

```markdown
## 受け入れ基準

| ID | 優先度 | 前提 | 操作 / 入力 | 期待結果 | 検証コマンド |
|----|--------|------|-------------|----------|--------------|
| AC-1 | Must | （環境・データ） | （ユーザー操作） | （観測可能な結果） | `（powershell または curl 1 行）` |
| AC-2 | Should | … | … | … | `…` |
```

## 記載ルール

| ルール | 内容 |
|--------|------|
| **AC-1 固定** | full-ui / 画面タッチ時は **代表 Happy path 1 本**を AC-1 Must に置く |
| **検証コマンド必須** | Must AC 各行に **再現可能な 1 コマンド**（qa-verifier がそのまま実行） |
| **優先度** | Must = 80% 達成に必須 · Should = 残り 20% の polish |
| **100% 到達** | `completion_target: 100` 時は Should **全行**必須 — [`delivery-completion-standard.md`](delivery-completion-standard.md) v2 · [`production-deploy-ac-template.md`](production-deploy-ac-template.md) |
| **禁止** | 「動作確認すること」等の非検証可能文言のみ |

## dev-reviewer ゲート

- Must AC に検証コマンド列が無い → **failed**（`category: acceptance_criteria`）
- AC 表自体が無い → **failed**

## 関連

- developer smoke: [`developer-smoke-template.md`](developer-smoke-template.md)
- qa evidence: `skills/development/qa-verifier/schemas/verification-result.v1.schema.json`
- 100% 本番デプロイ: [`production-deploy-ac-template.md`](production-deploy-ac-template.md)
- 100% エッジケース: [`edge-case-ac-checklist.md`](edge-case-ac-checklist.md)
- 100% SLA: [`production-sla-template.md`](production-sla-template.md)
