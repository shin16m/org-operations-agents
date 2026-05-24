# verification — 検証ドキュメント索引

このフォルダは **手順 / チェックリスト / 実行記録 / 固定 fixture** の 4 種類を含む。新規追加・読み解きの起点。

## 種類と使い分け

| 種類 | 例 | 役割 |
|------|-----|------|
| **手順（procedure）** | [`../e2e/default-workflow.md`](../e2e/default-workflow.md) · [`../e2e/dispatch-workflow.md`](../e2e/dispatch-workflow.md) | "どう実行するか"。SSOT |
| **smoke（チェックリスト）** | `*-smoke.md` | 組織変更・新機能リリース時に通す機械/目視チェック |
| **dryrun（実行記録）** | `*-dryrun.md` | 実際の実行ログ・Asana GID・所見 |
| **fixture（固定 JSON）** | [`fixtures/`](fixtures/) | dryrun スクリプトが読む再現用 Handoff / PlanReview |

## 索引

### 手順（このフォルダ外）

- [`../e2e/default-workflow.md`](../e2e/default-workflow.md) — default v3 標準手順
- [`../e2e/dispatch-workflow.md`](../e2e/dispatch-workflow.md) — execution 系子の dispatch ループ

### smoke（チェックリスト）

| ファイル | スコープ |
|----------|---------|
| [`planning-dept-v3-smoke.md`](planning-dept-v3-smoke.md) | 企画チーム L3 化・default v3 |
| [`development-pm-assignment-smoke.md`](development-pm-assignment-smoke.md) | 開発 PM 配賦・review rework |
| [`analytics-pm-assignment-smoke.md`](analytics-pm-assignment-smoke.md) | 分析 PM 配賦 |
| [`agent-comment-smoke.md`](agent-comment-smoke.md) | 署名付き comment / complete |
| [`org-dispatch-pm-smoke.md`](org-dispatch-pm-smoke.md) | dispatch → PM 配賦 |

### dryrun（最新を上）

| ファイル | 内容 |
|----------|------|
| [`all-teams-dryrun.md`](all-teams-dryrun.md) | 全チーム E2E（5 チーム × 全 enabled slug が complete まで到達。`audit` は組織変更時のみ） |
| [`planning-dept-v3-dryrun.md`](planning-dept-v3-dryrun.md) | default v3 ドライラン（企画チーム L3 化 + 開発 dispatch） |
| [`ux-delivery-v1-dryrun.md`](ux-delivery-v1-dryrun.md) | UX チーム + development full-ui |
| [`team-label-e2e-dryrun.md`](team-label-e2e-dryrun.md) | `チーム:` 表記移行検証 |
| [`e2e-dryrun.md`](e2e-dryrun.md) | E2E 基盤（v3 スコープ） |
| [`orchestrator-intake-dryrun.md`](orchestrator-intake-dryrun.md) | intake 入口化（v3） |
| [`asana-comment-detail-delivery.md`](asana-comment-detail-delivery.md) | コメント詳細化 epic · PM 代行事後補完（方針 B） |
| [`org-governance-audit-team-delivery.md`](org-governance-audit-team-delivery.md) | 監査チーム追加 epic · CI + L3 監査ゲート |
| [`asana-task-intake-dryrun.md`](asana-task-intake-dryrun.md) | Asana タスク起点 intake 窓口 · `intake_from_asana.py` |
| [`asana-comment-human-friendly-dryrun.md`](asana-comment-human-friendly-dryrun.md) | Asana コメント v1.2 二層形式 · 表示名マップ |
| [`asana-assignee-type-field-dryrun.md`](asana-assignee-type-field-dryrun.md) | 担当種別 CF · AI/human 自動設定 |

### archive（v2 以前の履歴）

| ファイル | 内容 |
|----------|------|
| [`archive/README.md`](archive/README.md) | 履歴索引 |
| [`archive/default-v2-dryrun.md`](archive/default-v2-dryrun.md) | default v2 |
| [`archive/orchestrator-intake-v2-dryrun.md`](archive/orchestrator-intake-v2-dryrun.md) | intake v2 |

### fixture

- [`fixtures/README.md`](fixtures/README.md) — 固定 Handoff / PlanReview の git 管理ポリシー

## 実行スクリプト

| script | 用途 |
|--------|------|
| [`../../tools/validate_org_registry.py`](../../tools/validate_org_registry.py) | registry ↔ workflow ↔ schema 整合 |
| [`../../tools/validate_fixture_schemas.py`](../../tools/validate_fixture_schemas.py) | fixture Handoff / PlanReviewResult の JSON Schema 検証 |
| [`../../tools/validate_ssot_contract.py`](../../tools/validate_ssot_contract.py) | SSOT 横断契約・禁止パターン検証 |
| [`../../tools/verify_consistency_audit_report.py`](../../tools/verify_consistency_audit_report.py) | ConsistencyAuditReport の live 再検証 |
| [`../../tools/check_epic_audit_gate.py`](../../tools/check_epic_audit_gate.py) | 監査子未完了の親 complete ブロック |
| [`../../tools/run_all_teams_dryrun.py`](../../tools/run_all_teams_dryrun.py) | 全チーム E2E dryrun（`all-teams-dryrun.md` を上書き生成） |

## 追加ルール（新規 dryrun / smoke 作成時）

1. **smoke は再実行可能なチェックリスト**にする（コマンド + 期待値）。記録は別の `*-dryrun.md` に分ける。
2. **dryrun には必須の冒頭ブロック**: 実施日 / Asana 親 GID + URL / 使用 fixture / コマンド全文。
3. **fixture は [`fixtures/`](fixtures/) のみに置く**。`output/` は実行時の書き出し先（gitignore）。
4. **v2 以前の履歴**は [`archive/`](archive/) に移す。現行 dryrun は v3 のみで書く。

## 関連

- 成果物ポリシー: [`../design/artifact-policy.md`](../design/artifact-policy.md)
- 組織モデル: [`../design/department-model.md`](../design/department-model.md)
- チーム取り決め: [`../design/team-conventions.md`](../design/team-conventions.md)
