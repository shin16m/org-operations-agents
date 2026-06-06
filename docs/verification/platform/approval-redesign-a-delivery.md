# 承認フロー再設計 A — Approval Result CF + 人間 assignee 連携 — delivery

| 項目 | 値 |
|------|------|
| Asana 親 epic | `1215102436561886` |
| Source Intake | `1215089495749122` |
| 関連 Intake (B / C) | `1215089409856284` / `1215102436390998` |
| 完了日 | 2026-05-25 |
| profile | lite |

## 概要

承認フロー再設計 3 分割の **A（土台）**。承認サブ起票時に必要な CF + 人間 assignee 連携を追加し、後続 B（承認ヘルパー）・C（Ready 再開ループ）の前提を整えた。**書込みのみ**のスコープに限定し、承認サブ完了検知 / Ready 復帰 / NG 分岐は B / C の別 Intake に分離。

## 変更点

### 実装

| ファイル | 変更 |
|---------|------|
| `tools/sync_org_os_cf_env.py` | `Approval Result` enum CF を **optional 検出**（OK/NG）。CF 未追加でも他 CF 同期は継続 |
| `skills/platform/asana-buddy/optional/asana_program_common.py` | `approval_result_config()` / `human_approver_gid()` / `assign_user(task_gid, user_gid, token)` 追加 |
| `skills/platform/asana-buddy/optional/create_approval_subtask.py` | 承認サブ作成と同時に **サブ assignee=人間** + **親 OS State=Waiting** + **親 Approval Required=Yes** を一括設定 |
| `skills/platform/asana-buddy/optional/.env.example` | `ASANA_APPROVAL_RESULT_*` 3 件 + `ASANA_DEFAULT_HUMAN_APPROVER_GID` 追記 |

### SSOT

| ファイル | 変更 |
|---------|------|
| `docs/design/approval-flow.md` | **新規** — 承認フロー全体 SSOT（CF 構成 / 起票時の動作 / 状態遷移 / A/B/C スコープ / env キー） |
| `docs/design/org-os-product-io.md` | §4.1 CF 表に Approval Result 追加 · §4.2 env 表に 4 キー追加 |
| `docs/design/planning-gate-vs-pm-review-gate.md` | 承認サブ作成時の親 CF 自動設定 + 人間 assignee 注記 + approval-flow.md 参照 |
| `skills/platform/asana-buddy/SKILL.md` | `create_approval_subtask` 行に CF / assignee 自動設定の説明追加 |

## 受け入れ条件

| # | 条件 | 結果 |
|---|------|------|
| 1 | `sync_org_os_cf_env --dry-run` で `Approval Result` 行出力 | ✅ 実機検証済 |
| 2 | `sync_org_os_cf_env --write -y` で env に 3 行追加 | ✅ 実機書込済（OK=...658602 / NG=...658603） |
| 3 | `create_approval_subtask` で「サブ assignee=人間 / 親 OS State=Waiting / 親 Approval Required=Yes」同時設定 | ✅ 静的検証 — 実呼び出しは B 実装時 E2E で検証 |
| 4 | CF / env 未設定でも警告のみで処理継続 | ✅ コード上で確認 |
| 5 | `validate_ssot_contract.py` 通過 | ✅ |

## レビュー結果

| review | status |
|--------|--------|
| `output/development/reviews/1215104963078378-code.review.json` | passed |
| `output/development/reviews/1215104963078378-verification.review.json` | passed |
| `output/governance/reviews/1215089843412777-governance.review.json` | passed |
| `output/audit/reviews/1215089843432109-audit.review.json` | passed |

## 次の Epic

| Epic | Intake GID | 内容 |
|------|------------|------|
| **B** 承認ヘルパー（監視・CF 更新） | `1215089409856284` | 承認サブ完了検知 → 親 `Approval Required=No` · `OS State=Ready` 自動戻し |
| **C** Ready 再開ループと NG 差し戻し | `1215102436390998` | OS State=Ready epic の自動 resume · `Approval Result=NG` 時の差し戻しループ · 上限到達時の escalation |

A 完了で **書込み（Waiting + Yes + assignee）** が揃ったので、次サイクルで B を着手すると承認フローが半閉路となる。

## 関連リンク

- 設計 SSOT: [`docs/design/approval-flow.md`](../design/approval-flow.md)
- Handoff: `output/planning/handoff/handoff.approval-redesign-a.json`
- Plan review: `output/planning/plan-review/plan-review.approval-redesign-a.json`
