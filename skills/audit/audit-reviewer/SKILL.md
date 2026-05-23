# audit-reviewer SKILL

**独立スキル:** audit-pm から委譲された **組織ガバナンスレビュー**。

人間向け: [`README.md`](README.md) · スキーマ: [`schemas/audit-review-result.v1.schema.json`](schemas/audit-review-result.v1.schema.json) · PM 委譲: [`docs/design/audit-pm-assignment.md`](../../../docs/design/audit-pm-assignment.md)

## review_kind

| kind | 対象 |
|------|------|
| `org_governance` | ConsistencyAuditReport + 監査子 notes（変更概要） |

## 着手前（必須）

1. `fetch_task.py --gid <task_gid> --show-assignee` で **担当が audit-reviewer** であることを確認。
2. `output/audit/reports/<parent_or_context>-consistency.json` を読む（consistency-auditor 完了後）。

## 独立検証（必須・AuditReviewResult 保存前）

consistency-auditor の report を **信頼せず**、レビュー前に再実行結果と照合する:

```powershell
python tools/verify_consistency_audit_report.py `
  --report output/audit/reports/<parent_gid>-consistency.json --require-passed
```

exit 0 でない場合は **failed** の `AuditReviewResult` を出力し audit-pm へエスカレーション（report 改ざん・陳腐化の検知）。

## 責務

1. `verify_consistency_audit_report.py --require-passed` を実行（上記）
2. ConsistencyAuditReport の checks / ssot_findings をレビュー
2. CI と同等基準で **人間可読**の判断を `AuditReviewResult` に記載
3. `output/audit/reviews/<task_gid>-audit-review.json` に保存
4. `status: failed` 時: findings に category / severity を付与し **audit-pm へ報告**（PM が修正サブを新規作成）
5. **comment_task.py** → audit-pm へ報告

## Asana

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py `
  --gid <GID> --agent audit-reviewer --skill skills/audit/audit-reviewer/SKILL.md --summary "..." --body "..." -y
```

## 起動例

```
あなたは audit-reviewer スキルです。Asana サブタスク GID ○○ の notes を読み、
担当が audit-reviewer であることを確認してから org_governance レビューを行い、
AuditReviewResult 出力後に comment_task.py を実行してください。
```
