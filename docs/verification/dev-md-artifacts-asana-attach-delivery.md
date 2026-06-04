# 開発 md 成果物 Asana 添付 — delivery 記録

| 項目 | 内容 |
|------|------|
| 実施 | 2026-06-04 |
| 親エピック GID | `1215422826609402` |
| ソース intake | `1215422825858038` |
| Handoff | `output/planning/handoff/handoff.dev-md-artifacts-asana-attach.json` |

## 子タスク

| # | GID | department | 状態 |
|---|-----|------------|------|
| 1/5 企画 | `1215423823977971` | planning | complete |
| 2/5 開発 | `1215424231906170` | development | complete |
| 3/5 開発 | `1215423945601121` | development | complete |
| 4/5 組織改善 | `1215423944957215` | governance | complete |
| 5/5 監査 | `1215423945733798` | audit | complete |

## 本体変更

| ファイル | 内容 |
|----------|------|
| `skills/platform/asana-buddy/optional/attach_task_files.py` | md 等の Asana attachment upload · `--list` |
| `skills/development/requirements-writer/SKILL.md` | attach 必須手順 |
| `skills/development/product-manager/SKILL.md` | PM complete 前 attach 確認 |
| `skills/development/dev-reviewer/SKILL.md` | attach 欠落 → failed |
| `docs/design/development-delivery-io.md` | 必須運用 · I/O 表 |
| `skills/development/examples/assign-plan.dev-md-attach-notes.md` | assign plan 補足 |

## 検証

```powershell
python skills/platform/asana-buddy/optional/attach_task_files.py --gid 1215424231906170 --file output/development/requirements/1215421282432324-requirements.md --dry-run
python tools/validate_org_registry.py
python tools/validate_ssot_contract.py
```

## 監査結果

| 成果物 | パス | status |
|--------|------|--------|
| ConsistencyAuditReport | `output/audit/reports/1215423945733798-consistency.json` | passed |
| AuditReviewResult | `output/audit/reviews/1215423945733798-audit-review.json` | passed |

## 教訓

- ローカル `output/development/` 保存だけでは依頼者が Asana 上で参照できない — attach を workflow 必須にした
- `lite` profile は spec skip 可 — requirements md の attach のみ必須
