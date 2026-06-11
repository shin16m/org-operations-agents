# 依頼者向け Epic 完了サマリ — テンプレート

| 版 | 1.0 |
| 日付 | 2026-06-11 |
| SSOT | `epic-completion-summary-template` |
| 関連 | [`delivery-completion-standard.md`](delivery-completion-standard.md) · [`comment_epic_summary.py`](../../skills/platform/asana-buddy/optional/comment_epic_summary.py) |

## 使い方

```powershell
python skills/platform/asana-buddy/optional/comment_epic_summary.py `
  --gid <PARENT_EPIC_GID> `
  --summary "Epic 完了 — 依頼者向けサマリ" `
  --render-template `
  --should-gaps-json docs/verification/fixtures/governance/should-gaps-sample.json `
  --verify-command "python tools/aggregate_delivery_kpi.py --parent <GID> --json" `
  --next-action "Should 未達 AC は follow-up Epic で polish" `
  -y
```

## 本文テンプレート（`--render-template` 時に組み立て）

```markdown
## 実施内容
- 本 Epic の execution 系子タスクを完了し、成果物をリポジトリに保存しました
- 完成度: {{COMPLETION_LEVEL}}（Must AC {{MUST_PASS_RATE}} · Should {{SHOULD_PASS_RATE}}）

## 成果物
{{ARTIFACTS_LIST}}

## Should AC 未達一覧
{{SHOULD_GAPS_TABLE}}

## 検証コマンド（依頼者が README のみで再現）
{{VERIFY_COMMANDS_LIST}}

## 次のアクション
{{NEXT_ACTIONS_LIST}}

## 次の状態
- 依頼者が上記検証コマンドで確認後、Epic を complete してください
```

### Should 未達表（`--should-gaps-json`）

JSON 配列。各要素:

| フィールド | 必須 | 説明 |
|------------|------|------|
| `ac_id` | ○ | AC 番号（例 `AC-3`） |
| `summary` | ○ | 未達内容（依頼者向け短文） |
| `verify_command` | 任意 | 再現コマンド |
| `priority` | 任意 | `Must` / `Should` |

## 完成度レベル記載ルール

| 条件 | `COMPLETION_LEVEL` |
|------|-------------------|
| Must 100% · Should ≥60% · smoke pass | ~80% |
| Should 100% · 本番運用 · polish | 100% |
| Should <60% または smoke 未達 | ~50–80%（未達を Should 表に明示） |
