# 監査チーム delivery I/O

workflow: [`workflows/audit-delivery.yaml`](../../workflows/audit-delivery.yaml) · 組織: [`department-model.md`](department-model.md)

## 位置づけ

| 項目 | 内容 |
|------|------|
| department id | `audit` |
| ラベル | 監査チーム |
| PM ハブ | audit-pm |
| ミッション | **組織定義変更**（workflow / registry / SSOT / rules）後の **全体整合性**を検証し、統制レポートを残す |

**二重防御:**

| 層 | タイミング | 手段 |
|----|------------|------|
| CI | 毎 PR / push | `validate_org_registry.py` · `validate_fixture_schemas.py` · `validate_ssot_contract.py` |
| L3 監査 | 組織変更エピックの execution 子 | audit-delivery（本書）— レポート + レビュー + Asana 記録 |

---

## いつ dispatch するか

企画 Handoff の execution 系子に **`department: audit`** を含める。典型:

- registry / workflow YAML 変更
- dispatch SSOT · cursor rule · 新 department 追加
- validate スクリプト追加・契約変更
- **SSOT / org-meta 横断整合**（governance 子あり · 定期整合性チェックエピック）

**配賦順:** governance（org-meta）の **後**、親エピック complete の **直前**（他 execution 系完了後 · [`department-model.md`](department-model.md) · [`workflow-io-contract.md`](workflow-io-contract.md)）。

---

## チーム内 workflow

```
audit-pm（intake · pm_assign）
  → consistency-auditor（機械検証 + ConsistencyAuditReport）
  → audit-reviewer（AuditReviewResult）
  → audit-pm（comment → complete → DeptWorkComplete）
```

assign plan 例: [`assign-plan.org-governance-v1.json`](../../skills/audit/examples/assign-plan.org-governance-v1.json)

---

## チーム内 I/O

| 成果物 | パス | 担当 |
|--------|------|------|
| ConsistencyAuditReport | `output/audit/reports/<task_gid>-consistency.json` | consistency-auditor |
| AuditReviewResult | `output/audit/reviews/<task_gid>-audit-review.json` | audit-reviewer |

### 機械検証（consistency-auditor 必須実行）

```powershell
python tools/validate_org_registry.py
python tools/validate_fixture_schemas.py
python tools/validate_ssot_contract.py
```

3 本すべて exit 0 が理想。`passed_with_notes` は audit-reviewer が許容可否を判断。

### 独立検証（audit-reviewer 必須）

```powershell
python tools/verify_consistency_audit_report.py --report output/audit/reports/<task_gid>-consistency.json --require-passed
```

report の `exit_code` が **live 再実行**と一致しない場合は failed 扱い。

### 親エピック complete 前（workflow-orchestrator）

Handoff に audit 子がある、または Asana に `チーム: audit` 子がある場合:

```powershell
python tools/check_epic_audit_gate.py --parent <親GID> [--handoff <path>]
```

---

## チーム間 I/O

| 方向 | 形式 |
|------|------|
| 入力 | `DispatchRequest` + 子 notes（監査対象・変更概要・done_when） |
| 出力 | `DeptWorkComplete` + `artifacts[]`（report / review JSON パス） |

**他チーム成果物を編集しない。** 読み取りは validate スクリプトと notes のみ。

---

## やらないこと

- 製品コード・Handoff 新規作成（→ 企画 / 開発）
- registry / workflow の **修正実装**（→ 開発子。監査は findings のみ）
- PM によるワーカー代行

---

## 参照

- PM 運用: [`audit-pm-assignment.md`](audit-pm-assignment.md)
- dispatch prompt: [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md#audit)
