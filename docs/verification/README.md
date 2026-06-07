# verification — 検証ドキュメント索引

このフォルダは **手順 / チェックリスト / 実行記録 / 固定 fixture** の 4 種類を含む。新規追加・読み解きの起点。

## レイアウト（チーム別）

| サブフォルダ | 対象 | 主な内容 |
|--------------|------|----------|
| [`platform/`](platform/) | **統括グループ** | intake · dispatch · Asana 運用 · 承認 · org-os · poller |
| [`planning/`](planning/) | **企画チーム** | Handoff · planning gate · review |
| [`development/`](development/) | **開発チーム** | PM 配賦 · dev workflow · review gate |
| [`ux/`](ux/) | **UX チーム** | ux-delivery v1/v2 |
| [`analysis/`](analysis/) | **分析チーム** | analysis-delivery v2 · profile 別 |
| [`governance/`](governance/) | **組織改善チーム** | SSOT 整合性 · project consistency |
| [`audit/`](audit/) | **監査チーム** | 監査チーム追加 · L3 監査ゲート |
| [`cross-team/`](cross-team/) | **チーム横断** | 全チーム E2E · UX→dev · 分析→dev |
| [`fixtures/`](fixtures/) | 固定 JSON | Handoff / PlanReview / audit report |
| [`archive/`](archive/) | 履歴 | v2 以前 |

**新規 dryrun / smoke / delivery** は上記チームフォルダのいずれかに置く（ルート直下には置かない）。

チーム別の設計・スキル・成果物パス: [`../design/team-conventions.md`](../design/team-conventions.md) § チーム別ファイルマップ

---

## 種類と使い分け

| 種類 | 例 | 役割 |
|------|-----|------|
| **手順（procedure）** | [`../e2e/default-workflow.md`](../e2e/default-workflow.md) · [`../e2e/dispatch-workflow.md`](../e2e/dispatch-workflow.md) | "どう実行するか"。SSOT |
| **smoke（チェックリスト）** | `*-smoke.md` | 組織変更・新機能リリース時に通す機械/目視チェック |
| **dryrun（実行記録）** | `*-dryrun.md` | 実際の実行ログ・Asana GID・所見 |
| **delivery（事後記録）** | `*-delivery.md` | エピック完了後の as-built 記録 |
| **fixture（固定 JSON）** | [`fixtures/`](fixtures/) | dryrun スクリプトが読む再現用 Handoff / PlanReview |

---

## チーム別クイックリンク

### platform（統括グループ）

| ファイル | 内容 |
|----------|------|
| [`orchestrator-intake-dryrun.md`](platform/orchestrator-intake-dryrun.md) | intake 入口化（v3） |
| [`org-dispatch-pm-smoke.md`](platform/org-dispatch-pm-smoke.md) | dispatch → PM 配賦 |
| [`agent-comment-smoke.md`](platform/agent-comment-smoke.md) | 署名付き comment / complete |
| [`asana-driven-ops-dryrun.md`](platform/asana-driven-ops-dryrun.md) | Asana ドリブン Phase 1 |
| [`approval-flow-e2e-dryrun.md`](platform/approval-flow-e2e-dryrun.md) | 承認フロー E2E |

→ 全件: [`platform/`](platform/) フォルダ参照

### planning（企画）

| ファイル | 内容 |
|----------|------|
| [`planning-dept-v3-smoke.md`](planning/planning-dept-v3-smoke.md) | 企画 L3 化 · default v3 |
| [`planning-dept-v3-dryrun.md`](planning/planning-dept-v3-dryrun.md) | default v3 ドライラン |
| [`subtask-review-gate-dryrun.md`](planning/subtask-review-gate-dryrun.md) | PM 委譲品質ゲート |

### development（開発）

| ファイル | 内容 |
|----------|------|
| [`development-pm-assignment-smoke.md`](development/development-pm-assignment-smoke.md) | PM 配賦 · review rework |
| [`dev-workflow-review-delivery.md`](development/dev-workflow-review-delivery.md) | dev workflow review |
| [`pm-review-gate-opt-in-delivery.md`](development/pm-review-gate-opt-in-delivery.md) | PM review gate opt-in |

### ux / analysis

| ファイル | 内容 |
|----------|------|
| [`ux-delivery-v2-dryrun.md`](ux/ux-delivery-v2-dryrun.md) | UX v2 flagship |
| [`analysis-delivery-v2-dryrun.md`](analysis/analysis-delivery-v2-dryrun.md) | 分析 v2 full |
| [`analytics-pm-assignment-smoke.md`](analysis/analytics-pm-assignment-smoke.md) | 分析 PM 配賦 |

### governance / audit

| ファイル | 内容 |
|----------|------|
| [`governance-audit-consistency-dryrun.md`](governance/governance-audit-consistency-dryrun.md) | SSOT 整合性 |
| [`org-governance-audit-team-delivery.md`](audit/org-governance-audit-team-delivery.md) | 監査チーム追加 epic |

### cross-team（横断）

| ファイル | 内容 |
|----------|------|
| [`all-teams-dryrun.md`](cross-team/all-teams-dryrun.md) | 全チーム E2E（6 チーム） |
| [`e2e-dryrun.md`](cross-team/e2e-dryrun.md) | E2E 基盤（v3） |
| [`ux-to-dev-full-ui-dryrun.md`](cross-team/ux-to-dev-full-ui-dryrun.md) | UX → development 継ぎ目 |
| [`analysis-to-dev-dryrun.md`](cross-team/analysis-to-dev-dryrun.md) | 分析 → development 継ぎ目 |

---

## 手順（このフォルダ外）

- [`../e2e/default-workflow.md`](../e2e/default-workflow.md) — default v3 標準手順
- [`../e2e/dispatch-workflow.md`](../e2e/dispatch-workflow.md) — execution 系子の dispatch ループ

## archive（v2 以前）

| ファイル | 内容 |
|----------|------|
| [`archive/README.md`](archive/README.md) | 履歴索引 |
| [`archive/default-v2-dryrun.md`](archive/default-v2-dryrun.md) | default v2 |
| [`archive/orchestrator-intake-v2-dryrun.md`](archive/orchestrator-intake-v2-dryrun.md) | intake v2 |

## fixture

- [`fixtures/README.md`](fixtures/README.md) — 固定 Handoff / PlanReview の git 管理ポリシー

---

## 実行スクリプト

| script | 用途 |
|--------|------|
| [`../../tools/validate_org_registry.py`](../../tools/validate_org_registry.py) | registry ↔ workflow ↔ schema 整合 |
| [`../../tools/validate_fixture_schemas.py`](../../tools/validate_fixture_schemas.py) | fixture Handoff / PlanReviewResult の JSON Schema 検証 |
| [`../../tools/validate_ssot_contract.py`](../../tools/validate_ssot_contract.py) | SSOT 横断契約・禁止パターン検証 |
| [`../../tools/run_all_teams_dryrun.py`](../../tools/run_all_teams_dryrun.py) | 全チーム E2E（`cross-team/all-teams-dryrun.md` を生成） |
| [`../../tools/run_ux_v2_dryrun.py`](../../tools/run_ux_v2_dryrun.py) | UX v2 単体 dryrun |
| [`../../tools/run_analysis_v2_dryrun.py`](../../tools/run_analysis_v2_dryrun.py) | 分析 v2 full 単体 dryrun |
| [`../../tools/run_ux_to_dev_full_ui_dryrun.py`](../../tools/run_ux_to_dev_full_ui_dryrun.py) | UX → dev full-ui 継ぎ目 |
| [`../../tools/run_analysis_profile_dryrun.py`](../../tools/run_analysis_profile_dryrun.py) | 分析 profile 別 dryrun |
| [`../../tools/run_analysis_to_dev_dryrun.py`](../../tools/run_analysis_to_dev_dryrun.py) | 分析 → dev 継ぎ目 |
| [`../../tools/check_new_department.py`](../../tools/check_new_department.py) | 新チーム checklist A〜J |
| [`../../tools/check_new_skill.py`](../../tools/check_new_skill.py) | 新規 slug 配線チェック |
| [`../../tools/asana_ops_poller.py`](../../tools/asana_ops_poller.py) | Asana スキャン · intake trigger（[`asana-driven-ops.md`](../design/asana-driven-ops.md)） |

その他 PM gate · intake · レトロ系: 各 dryrun 記録の「コマンド」節を参照。

---

## 追加ルール（新規 dryrun / smoke 作成時）

1. **配置:** `docs/verification/<dept>/` に置く（`platform` | `planning` | `development` | `ux` | `analysis` | `governance` | `audit` | `cross-team`）。
2. **smoke は再実行可能なチェックリスト**にする（コマンド + 期待値）。記録は別の `*-dryrun.md` に分ける。
3. **dryrun には必須の冒頭ブロック**: 実施日 / Asana 親 GID + URL / 使用 fixture / コマンド全文。
4. **fixture は [`fixtures/`](fixtures/) のみ**に置く。`output/` は実行時の書き出し先（gitignore）。
5. **v2 以前の履歴**は [`archive/`](archive/) に移す。
6. **doc-only validate 節:** profile: doc-only の dryrun / delivery / smoke は [`_templates/doc-only-validate-section.md`](_templates/doc-only-validate-section.md) を validate 節の SSOT とする。テンプレをコピーし、§3.2 形式の実行結果表（判定・理由列）を必ず記載する。
7. **doc-only 既定表:** 下記とテンプレ末尾の参照表を整合させること。

| コマンド | doc-only 既定 | skip 許容例 |
|----------|---------------|-------------|
| `validate_org_registry.py` | **実行** | registry / workflow YAML 未変更かつ事前確認済み |
| `validate_fixture_schemas.py` | fixture 変更時のみ | fixture 未変更の doc-only |
| `validate_ssot_contract.py` | **実行** | SSOT 契約未変更かつ事前確認済み（稀） |

8. **新規 doc-only 記録:** dryrun / delivery 作成時は上記テンプレを validate 節として組み込み、3 コマンドすべてを実行結果表に含める（実行・skip 混在可）。skip 時は理由を 1 文以上記載する。

---

## 関連

- 成果物ポリシー: [`../design/artifact-policy.md`](../design/artifact-policy.md)
- 組織モデル: [`../design/department-model.md`](../design/department-model.md)
- チーム取り決め: [`../design/team-conventions.md`](../design/team-conventions.md)
