# 承認タスクのメッセージ改善 — delivery

| 項目 | 内容 |
|------|------|
| epic | `1215478309435355` |
| 企画子 | `1215465103424265` |
| 開発子 | `1215465187156879` |
| intake ソース | `1215464025562097` |

## 変更ファイル

| ファイル | 変更 |
|----------|------|
| `skills/platform/asana-buddy/optional/create_approval_subtask.py` | `_post_approval_mention` の HTML 本文に `Approval Result=OK/NG` 操作案内を追記 |
| 同上 | `--notes` 未指定時のデフォルト notes に同内容を追記（旧「完了 = 承認」表現を廃止） |
| `output/planning/handoff/handoff.approval-message-improvement.json` | 本 epic Handoff |
| `output/planning/plan-review/plan-review.approval-message-improvement.json` | PlanReviewResult（passed） |

## SSOT 整合

[`docs/design/approval-flow.md`](../design/approval-flow.md) §3 の人間操作と一致:

| 結果 | 操作 |
|------|------|
| OK | `Approval Result=OK` を選択 → 完了 |
| NG | コメント追記 → `Approval Result=NG` を選択 → 完了 |

## 確認手順

1. テスト用親タスク（または dry-run）で承認サブを作成:

```powershell
python skills/platform/asana-buddy/optional/create_approval_subtask.py `
  --parent <TEST_PARENT_GID> --title "【承認】メッセージ改善確認" --dry-run
```

2. 本番起票（`-y`）後、Asana UI で以下を確認:
   - サブ **notes** に `Approval Result=OK` / `NG` の手順が記載されている
   - サブ **コメント**（@mention story）に同様の OK/NG 案内が含まれる
3. `Approval Result=OK` 選択 → complete → `approval_helper --once` で親が Ready に戻ること（既存 B フロー）

## スコープ外

- `create_pm_review_gate.py`（PM review gate）は本 epic 対象外
