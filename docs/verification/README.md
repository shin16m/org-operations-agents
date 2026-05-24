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
| [`asana-driven-auto-intake-dryrun.md`](asana-driven-auto-intake-dryrun.md) | Phase 4 auto-intake · CLI baseline · Cursor SDK PoC |
| [`cf400-workaround-dryrun.md`](cf400-workaround-dryrun.md) | CF 400 workaround · sync_assignee_type_env CLI |
| [`asana-driven-ops-phase3-dryrun.md`](asana-driven-ops-phase3-dryrun.md) | Asana ドリブン Phase 3 · Webhook · ダッシュボード MVP |
| [`asana-driven-ops-phase2-dryrun.md`](asana-driven-ops-phase2-dryrun.md) | Asana ドリブン Phase 2 · gate 統合 · マルチプロジェクト · RESUME snippet |
| [`asana-driven-ops-dryrun.md`](asana-driven-ops-dryrun.md) | Asana ドリブン運用 · poller / suspend CLI · Phase 1 |
| [`asana-pm-ops-hardening-dryrun.md`](asana-pm-ops-hardening-dryrun.md) | PM review gate · worker CF · validate 強化 |
| [`epic-retrospective-intake-dryrun.md`](epic-retrospective-intake-dryrun.md) | エピック完了前レトロ → intake タスク化 |
| [`subtask-review-gate-dryrun.md`](subtask-review-gate-dryrun.md) | PM 委譲品質ゲート + 企画ブラッシュアップ |
| [`epic-ops-quality-dryrun.md`](epic-ops-quality-dryrun.md) | bootstrap 重複防止 · PM 委譲 · エピック完了サマリ |
| [`governance-audit-consistency-dryrun.md`](governance-audit-consistency-dryrun.md) | governance + audit 主体の SSOT 整合性チェック |
| [`org-improvement-governance-team-dryrun.md`](org-improvement-governance-team-dryrun.md) | 組織改善チーム governance 追加 |
| [`project-consistency-check-dryrun.md`](project-consistency-check-dryrun.md) | 定期 SSOT 整合性チェック · validate 4 本 |
| [`asana-intake-comments-dryrun.md`](asana-intake-comments-dryrun.md) | intake-asana snapshot v1.1 · コメント stories |
| [`intake-source-task-closure-dryrun.md`](intake-source-task-closure-dryrun.md) | intake 元タスク comment+complete |
| [`asana-subtask-layout-fix-dryrun.md`](asana-subtask-layout-fix-dryrun.md) | サブタスク addProject 撤回 |
| [`all-teams-dryrun.md`](all-teams-dryrun.md) | 全チーム E2E（6 チーム × enabled slug · `audit` は組織変更時のみ） |
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
| [`../../tools/check_new_department.py`](../../tools/check_new_department.py) | 新 department 追加チェックリスト |
| [`../../tools/create_pm_review_gate.py`](../../tools/create_pm_review_gate.py) | PM assign 後の人間レビューゲート作成 |
| [`../../tools/check_pm_review_gate.py`](../../tools/check_pm_review_gate.py) | PM レビューゲート承認 polling |
| [`../../skills/platform/asana-buddy/optional/create_approval_subtask.py`](../../skills/platform/asana-buddy/optional/create_approval_subtask.py) | 汎用承認サブ作成 |
| [`../../skills/platform/asana-buddy/optional/check_approval_subtask.py`](../../skills/platform/asana-buddy/optional/check_approval_subtask.py) | 汎用承認サブ polling |
| [`../../tools/intake_from_asana.py`](../../tools/intake_from_asana.py) | intake-asana snapshot 取得 |
| [`../../skills/platform/asana-buddy/optional/close_intake_source_task.py`](../../skills/platform/asana-buddy/optional/close_intake_source_task.py) | intake 元タスククローズ |
| [`../../skills/platform/asana-buddy/optional/comment_epic_summary.py`](../../skills/platform/asana-buddy/optional/comment_epic_summary.py) | エピック complete 前サマリ |
| [`../../tools/backfill_subtask_project_membership.py`](../../tools/backfill_subtask_project_membership.py) | 誤配置サブタスク removeProject |
| [`../../tools/run_all_teams_dryrun.py`](../../tools/run_all_teams_dryrun.py) | 全チーム E2E dryrun（`all-teams-dryrun.md` を上書き生成） |
| [`../../tools/aggregate_epic_retrospective.py`](../../tools/aggregate_epic_retrospective.py) | エピック単位レトロ候補の集約 |
| [`../../tools/create_retrospective_intake_gate.py`](../../tools/create_retrospective_intake_gate.py) | 【承認】レトロ改善候補サブ作成 |
| [`../../tools/check_retrospective_intake_gate.py`](../../tools/check_retrospective_intake_gate.py) | レトロ intake 承認 gate 確認 |
| [`../../tools/create_retrospective_intake_tasks.py`](../../tools/create_retrospective_intake_tasks.py) | レトロ候補から intake タスク起票 |
| [`../../tools/asana_ops_poller.py`](../../tools/asana_ops_poller.py) | Asana スキャン · intake trigger · 保留監視（[`asana-driven-ops.md`](../design/asana-driven-ops.md)） |
| [`../../tools/check_workflow_suspend.py`](../../tools/check_workflow_suspend.py) | SuspendedSession 一覧 / gate 状態確認 |

## 追加ルール（新規 dryrun / smoke 作成時）

1. **smoke は再実行可能なチェックリスト**にする（コマンド + 期待値）。記録は別の `*-dryrun.md` に分ける。
2. **dryrun には必須の冒頭ブロック**: 実施日 / Asana 親 GID + URL / 使用 fixture / コマンド全文。
3. **fixture は [`fixtures/`](fixtures/) のみに置く**。`output/` は実行時の書き出し先（gitignore）。
4. **v2 以前の履歴**は [`archive/`](archive/) に移す。現行 dryrun は v3 のみで書く。

## 関連

- 成果物ポリシー: [`../design/artifact-policy.md`](../design/artifact-policy.md)
- 組織モデル: [`../design/department-model.md`](../design/department-model.md)
- チーム取り決め: [`../design/team-conventions.md`](../design/team-conventions.md)
