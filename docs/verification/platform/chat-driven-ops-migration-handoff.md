# Asana 自動化 / org-os 廃止 — セッション引継ぎ

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-09 |
| ブランチ | `2-delete-asana-driven` |
| 状態 | 作業完了 · **未 push**（origin より 3+ コミット先行） |
| 本番 SSOT | [`docs/design/chat-driven-ops.md`](../../design/chat-driven-ops.md) |

## 目的（達成済）

**token コスト制約**のため、Asana 上のタスクを**自動検出してエージェントを起動する機能**（Asana 自動化）と org-os watch 連携を本番から切り離した。

- **廃止:** Intake 自動検出 · watch 常駐 · poller/runner · `--record-wait` · 再開ループ
- **継続:** Asana タスクの作成・遂行（`handoff_to_asana` · `comment_task` / `complete_task` · `task_dispatcher`）
- **本番入口:** Cursor チャットで **和久桶さん**（`workflow-orchestrator`）へ自然言語依頼

## コミット履歴（この作業分）

| SHA | メッセージ | 概要 |
|-----|-----------|------|
| `51278b0` | `fix(ops): Asana自動化を廃止しチャット入口を本番標準に固定` | 本丸 — `asana_ops_*` · watch 等大量削除 · `default.yaml` v6 · `chat-driven-ops.md` |
| `f670ad3` | `fix(ops): 廃止済み auto-intake ツールとスタブテストを削除` | `auto_intake_runner` · `cursor_intake_dispatch` · スタブテスト · `_common.ps1` 整理 |
| `ae4b8cd` | `fix(ops): 廃止後の SKILL 整合と再開ループツールを削除` | SKILL 修正 · `complete_task` org-os 除去 · 再開ループ CLI 削除 · validate 強化 |

**差分規模（main から）:** 約 84 ファイル · +1,538 / -4,341 行

## 本番 SSOT 一覧

| パス | 役割 |
|------|------|
| [`docs/design/chat-driven-ops.md`](../../design/chat-driven-ops.md) | 本番運用 SSOT |
| [`docs/design/workflow-io-contract.md`](../../design/workflow-io-contract.md) | パイプライン段階定義 |
| [`workflows/default.yaml`](../../../workflows/default.yaml) v6 | 宣言的 workflow（org-os suspend/resume なし） |
| [`.cursor/rules/workflow-intake-required.mdc`](../../../.cursor/rules/workflow-intake-required.mdc) | エージェント制約 |
| [`tools/_retired/README.md`](../../../tools/_retired/README.md) | 削除済み自動化ツール索引 |
| [`products/_retired/README.md`](../../../products/_retired/README.md) | org-os パッケージ索引（コード残置） |

## 削除済みツール

| パス | 役割 |
|------|------|
| `tools/asana_ops_poller.py` | Intake 自動検出 · RESUME スキャン |
| `tools/asana_ops_runner.py` | watch 常駐 runner |
| `tools/asana_ops_dashboard.py` | WAIT/RESUME UI |
| `tools/asana_ops_sessions.py` | session JSON |
| `tools/asana_webhook_handler.py` | Webhook ハンドラ |
| `tools/auto_intake_runner.py` | CLI auto-bootstrap |
| `tools/cursor_intake_dispatch.py` | SDK intake 自動 kick |
| `tools/approval_helper.py` | 承認サブ完了監視 + 親 CF 復帰 |
| `tools/wakuoke_resume_scan.py` | Ready epic 再開スキャン |
| `tools/check_workflow_suspend.py` | SuspendedSession（`--record-wait`） |
| `tools/pm_emit_resume_prompt.py` | RESUME 再開 snippet |
| `tools/bypass_planning_gate.py` | org-os syscall 経由 gate bypass |
| `scripts/org-ops/org-ops-watch*` | watch 起動 |
| `scripts/org-ops/org-ops-webhook*` | Webhook 常駐 |
| `scripts/org-ops/org-ops-once-dryrun*` | poller dry-run |

## 主要な修正（ae4b8cd 以降）

| 対象 | 変更 |
|------|------|
| `skills/planning/planning-pm/SKILL.md` | opt-in gate をチャット確認フローに（`asana_ops_poller` / `org-ops-watch` 記述削除） |
| `skills/platform/asana-buddy/SKILL.md` · `README.md` | org-os 自動 complete 記述削除 · 廃止ツールを索引へ |
| `skills/platform/asana-buddy/optional/complete_task.py` | `run_org_os.py complete` 連動を除去（レトロ hook のみ） |
| `docs/design/approval-flow.md` | B/C 段階を **RETIRED / 削除済** に更新 |
| `tools/validate_ssot_contract.py` | `planning-pm` · `asana-buddy` を active チェック対象に追加 |
| `products/org-os/README.md` | watch 手順除去 · doctor のみ |
| `docs/verification/platform/README.md` | active / RETIRED 索引 |
| `docs/verification/platform/chat-driven-ops-dryrun.md` | 移行 dryrun 実行記録 |
| `tools/test_cursor_sdk_kick.py` | cursor_sdk 未インストール環境でも pass |
| `tools/check_milestone_readiness.py` | subprocess UTF-8 `errors=replace` |

## 意図的に残しているもの（任意・後続）

| 残置物 | 備考 |
|--------|------|
| `products/org-os/` 全体 | 履歴参照 · `python tools/run_org_os.py doctor` |
| `run_org_os.py` · `complete_epic_os_state.py` · `sync_org_os_cf_env.py` | 非推奨ラッパー |
| `execution_resume_scan.py` · `execution_kick_guard.py` | 手動 dev dispatch 用（[`tools/_retired/README.md`](../../../tools/_retired/README.md)） |
| `scripts/org-ops/setup.ps1` · `org-ops-dispatch.*` | venv 初期化 · 手動 `task_dispatcher --kick` |
| `create_approval_subtask.py` | opt-in 【承認】サブ（OS State CF 書込あり） |
| `docs/verification/platform/*` RETIRED 注記付き | 履歴参照 · 索引は [`platform/README.md`](README.md) |
| `docs/design/asana-driven-ops.md` · `org-os-product-io.md` | RETIRED 設計 SSOT |

## 検証

```powershell
python tools/validate_ssot_contract.py
# OK - SSOT cross-document contracts satisfied.

python -m unittest tools.test_complete_task_epic tools.test_execution_resume_scan
# OK

python -m unittest discover -s tools -p "test_*.py"
# 127 件 — OK（全 green）
```

詳細記録: [`chat-driven-ops-dryrun.md`](chat-driven-ops-dryrun.md)

## 自己評価（観点別）

| 観点 | 評価 | コメント |
|------|------|----------|
| 方針・SSOT | **A** | `chat-driven-ops.md` が本番入口 SSOT · validate 契約 pass |
| コード削除 | **A** | 自動化コア除去完了 · org-os 本体は `_retired` 索引付き残置 · watch 手順除去 |
| エージェント手順整合 | **A** | 必須 SKILL 修正済 · `validate_ssot_contract` で検出 |
| 回帰防止 | **A-** | validate 3 本 + unittest 127/127 · CI validate workflow green 待ち |
| ドキュメント整理 | **A** | `platform/README.md` で active/RETIRED 分離 · 残存 automation doc に RETIRED 注記 |
| 運用移行の実証 | **A** | `chat-driven-ops-dryrun.md` に validate 実行記録 + prior E2E 証跡リンク |
| 作業の締まり | **A** | 本セッション分コミット済 · working tree clean |

## 次セッション TODO（優先順）

1. `git push -u origin 2-delete-asana-driven` → PR 作成・マージ
2. （任意）`execution_resume_scan` 削除 · `products/org-os/` 完全削除
3. （任意）RETIRED verification doc を `docs/verification/archive/platform-automation/` へ物理移動（リンク更新要）

## 和久桶さんへの依頼テンプレ（本番）

```
和久桶さん、次の課題をお願いします。

〈自然言語で依頼内容〉

intake から bootstrap → 企画（Handoff → review → gate）→ Asana 投入 → execution 系 dispatch まで進めてください。
```

## 関連（廃止ドキュメント）

| 旧 SSOT | 状態 |
|---------|------|
| [`asana-driven-ops.md`](../../design/asana-driven-ops.md) | RETIRED |
| [`org-os-product-io.md`](../../design/org-os-product-io.md) | DEPRECATED · RETIRED |
| [`docs/e2e/org-ops-watch-runbook.md`](../../e2e/org-ops-watch-runbook.md) | RETIRED |
