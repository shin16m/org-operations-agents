# ssot-implementer SKILL

人間向け: [`README.md`](README.md) · persona: [`personas/ssot_implementer.md`](personas/ssot_implementer.md)

**独立スキル:** governance-pm から委譲された **org-meta / SSOT 実装**。

人間向け: [`README.md`](README.md) · PM 委譲: [`docs/design/governance-pm-assignment.md`](../../../docs/design/governance-pm-assignment.md)

## 着手前（必須）

`fetch_task.py --gid <task_gid> --show-assignee` で **担当が ssot-implementer** であることを確認。

## 責務

1. 親エピック notes · Handoff スコープに従い registry / skills / workflow / docs / tools を変更
2. 実装後に validate 3 本を実行:

```powershell
python tools/validate_org_registry.py
python tools/validate_fixture_schemas.py
python tools/validate_ssot_contract.py
```

3. 任意: `output/governance/records/<task_gid>-record.md` に変更一覧
4. **comment_task.py** → governance-pm へ報告

## やらないこと

- Handoff 新規作成（→ 企画）
- GovernanceReviewResult 作成（→ governance-reviewer）
- 製品アプリコード（→ developer）
