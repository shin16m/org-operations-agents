# workflow-orchestrator SKILL

**独立スキル:** 宣言的 workflow + agent-registry に基づく段階案内（`orchestrate` スロット）。ビジネスロジックは各スキルに委譲。

## 参照ファイル（読むだけ・編集は人間の PR）

| ファイル | 内容 |
|----------|------|
| [`workflows/default.yaml`](../../workflows/default.yaml) | 段階順・ゲート ID |
| [`workflows/agent-registry.yaml`](../../workflows/agent-registry.yaml) | slug・slot・I/O 参照 |
| [`docs/design/workflow-io-contract.md`](../../docs/design/workflow-io-contract.md) | I/O・ゲート定義 |

## 責務

1. 現段階（plan / review / orchestrate / execute）の判定
2. ゲート `review_passed`・`handoff_approved` の満足確認
3. **次に呼ぶスキル**と Copilot/Cursor 用の短い起動プロンプト例
4. registry 未登録 slug → 明示エラー + CONTRIBUTING の拡張手順を案内

## review 必須（ワークフロー政策）

[`workflows/default.yaml`](../../workflows/default.yaml) の `policy.review_required: true` に従う。

- **`plan-reviewer` を経ていない Handoff は `execute` に進めない。**
- `PlanReviewResult` が無い、または `status` が `needs_revision` / `blocked` のときは [`plan-reviewer`](../plan-reviewer/SKILL.md) または `plan` へ差し戻す。
- 人間が「確認した」と言っただけでは `review_passed` とみなさない。

## やらないこと

- Handoff の新規作成（→ issue-story-planner）
- プランの詳細レビュー（→ plan-reviewer）
- Asana API 実行（→ asana-buddy）
- **新規 `skills/<slug>/` の生成（→ agent-creater のみ）**

## 新規エージェント作成

利用者が新スキルを求めたら、必ず [`agent-creater`](../agent-creater/SKILL.md) を案内する。registry / workflow 更新は人間の PR。

## 出力（モデル向け）

Markdown 短い要約 + 次アクション:

- `current_step` / `next_agent` / `gate_status`
- `prompt_snippet`（次スキル用 1 段落）
- ブロック時は `blocked_reason` と戻り先段階

## 起動例

```
あなたは workflow-orchestrator スキルです。PlanReviewResult と Handoff が渡されます。
workflows/default.yaml に従い、execute に進めるか、差し戻し先を示してください。
```
