# consistency-auditor SKILL

**独立スキル:** audit-pm から委譲された **機械整合性検証**。

人間向け: [`README.md`](README.md) · スキーマ: [`schemas/consistency-audit-report.v1.schema.json`](schemas/consistency-audit-report.v1.schema.json) · PM 委譲: [`docs/design/audit-pm-assignment.md`](../../../docs/design/audit-pm-assignment.md)

## 着手前（必須）

1. `fetch_task.py --gid <task_gid> --show-assignee` で **担当が consistency-auditor** であることを確認。
2. 不一致なら作業せず audit-pm へエスカレーション。

## 責務

1. リポジトリ root で以下 3 本を **順に実行**し exit code を記録:

```powershell
python tools/validate_org_registry.py
python tools/validate_fixture_schemas.py
python tools/validate_ssot_contract.py
```

2. `ConsistencyAuditReport` JSON を `output/audit/reports/<task_gid>-consistency.json` に保存
3. `validate_ssot_contract.py` の stderr / 出力から `ssot_findings[]` を抽出（あれば）
4. **comment_task.py** → audit-pm へ報告

audit-reviewer は保存後に `tools/verify_consistency_audit_report.py` で **live 再検証**する（[`audit-reviewer/SKILL.md`](../audit-reviewer/SKILL.md)）。

### status 判定

| 条件 | status |
|------|--------|
| 3 本すべて exit 0 | `passed` |
| exit 0 だが ssot_findings に medium/low のみ | `passed_with_notes`（reviewer 判断） |
| いずれか exit 非 0 | `failed` |

## Asana

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py `
  --gid <GID> --agent consistency-auditor --skill skills/audit/consistency-auditor/SKILL.md --summary "..." --body "..." -y
```

## やらないこと

- registry / workflow / SSOT の **修正実装**（findings のみ）
- audit-reviewer のレビュー（→ audit-reviewer サブタスク）
