# 承認フロー再設計 B — 承認ヘルパー（監視・CF 更新）— delivery

| 項目 | 値 |
|------|------|
| Asana 親 epic | `1215102437909462` |
| Source Intake | `1215089409856284` |
| 関連 (A 完了 / C 進行中) | `1215102436561886` / `1215102436390998` |
| 完了日 | 2026-05-25 |
| profile | lite |

## 概要

A の起票時設定（人間 assignee + 親 OS State=Waiting + Approval Required=Yes）を**逆方向に戻す**承認ヘルパー CLI を新設。承認サブの完了をポーリング検知し、`Approval Result` enum を読取って親エピックを Ready/No に戻す。

## 変更点

### 実装

| ファイル | 変更 |
|---------|------|
| `tools/approval_helper.py` | **新規** — `--parent` / `--approval-sub` / `--gate-kind` / `--once` / `--interval` / `--timeout` / `--log-dir` でオンデマンド監視 |
| `skills/platform/asana-buddy/optional/asana_program_common.py` | `get_task_custom_fields` / `read_approval_result` 追加 |

### SSOT

| ファイル | 変更 |
|---------|------|
| `docs/design/approval-flow.md` | §5 表で B を実装済に書換 · §5.1 CLI 仕様 / exit code / ログ JSON · §5.2 関連実装関数を追加 |
| `docs/design/asana-driven-ops.md` | Tools 表に `approval_helper.py` 行追加 + create_approval_subtask 説明補強 |
| `skills/platform/asana-buddy/SKILL.md` | `approval_helper.py` を CLI 表に追記 |

## 受け入れ条件

| # | 条件 | 結果 |
|---|------|------|
| 1 | `--help` がエラー無く表示 | ✅ |
| 2 | missing subtask で exit=2 | ✅ |
| 3 | pending で exit=1（`--once`、ログ未保存） | ✅ 静的検証 |
| 4 | approved で exit=0 + 親 CF Ready/No + ログ JSON 出力 | ✅ 静的検証 — E2E は C で |
| 5 | CF/env 未設定でも警告のみで継続 | ✅ コードで確認 |
| 6 | `validate_ssot_contract.py` 通過 | ✅ |

## レビュー結果

| review | status |
|--------|--------|
| `output/development/reviews/1215089739061676-code.review.json` | passed |
| `output/development/reviews/1215089739061676-verification.review.json` | passed |
| `output/governance/reviews/1215089810487376-governance.review.json` | passed |
| `output/audit/reviews/1215089608317887-audit.review.json` | passed |

## 次の Epic

**C** Ready 再開ループと NG 差し戻し（Intake `1215102436390998`）— OS State=Ready epic の和久桶自動再開と `Approval Result=NG` 時のループ実装。

## 関連リンク

- 設計 SSOT: [`docs/design/approval-flow.md`](../design/approval-flow.md) §5
- Handoff: `output/planning/handoff/handoff.approval-redesign-b.json`
- Plan review: `output/planning/plan-review/plan-review.approval-redesign-b.json`
