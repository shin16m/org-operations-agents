# chat-driven-ops 移行 dryrun — 実行記録

| 項目 | 内容 |
|------|------|
| 実施日 | 2026-06-09 |
| ブランチ | `2-delete-asana-driven` |
| 本番 SSOT | [`docs/design/chat-driven-ops.md`](../../design/chat-driven-ops.md) |
| 手順 SSOT | [`docs/e2e/default-workflow.md`](../../e2e/default-workflow.md) v6 |
| 引継ぎ | [`chat-driven-ops-migration-handoff.md`](chat-driven-ops-migration-handoff.md) |

## 目的

Asana 自動化（poller / watch / runner / `--record-wait` / 再開ループ）廃止後、**チャット入口**（和久桶さん `workflow-orchestrator`）が SSOT・SKILL・validate と整合し、回帰テストが green であることを機械的に確認する。

## 検証範囲

| 区分 | 確認内容 | 結果 |
|------|----------|------|
| 方針 | `chat-driven-ops.md` が本番入口 SSOT | pass |
| コード削除 | `asana_ops_*` · watch スクリプト不在 | pass |
| SKILL | `planning-pm` · `asana-buddy` に poller/watch 記述なし | pass（validate 契約） |
| 回帰 | unittest 127/127 · validate_ssot | pass |
| パイプライン | v3 dryrun 記録が現行手順と整合 | pass（下記参照） |

## validate（doc-only）

### 実行コマンド

```powershell
cd E:\data\document\sourse\org-operations-agents
$env:PYTHONIOENCODING='utf-8'
python tools/validate_org_registry.py
python tools/validate_fixture_schemas.py
python tools/validate_ssot_contract.py
python -m unittest discover -s tools -p "test_*.py"
python -m unittest tools.test_complete_task_epic tools.test_execution_resume_scan
```

### 実行結果

| コマンド | 判定 | exit | 理由 |
|----------|------|------|------|
| `validate_org_registry.py` | 実行 | 0 | registry ↔ workflow 整合 |
| `validate_fixture_schemas.py` | 実行 | 0 | fixture JSON Schema pass |
| `validate_ssot_contract.py` | 実行 | 0 | chat-driven 契約 · 廃止パターン検出 pass |
| `unittest discover` | 実行 | 0 | **127 tests OK** |
| `test_complete_task_epic` + `test_execution_resume_scan` | 実行 | 0 | complete_task org-os 除去後も pass |

## 廃止確認（削除済みツール）

以下がリポジトリに **存在しない** ことを確認（`validate_ssot_contract.py` FORBIDDEN パターン + 手動 `Test-Path`）:

| パス | 状態 |
|------|------|
| `tools/asana_ops_poller.py` | 削除済 |
| `tools/asana_ops_runner.py` | 削除済 |
| `tools/asana_webhook_handler.py` | 削除済 |
| `scripts/org-ops/org-ops-watch.ps1` | 削除済 |
| `tools/check_workflow_suspend.py` | 削除済 |

索引: [`tools/_retired/README.md`](../../../tools/_retired/README.md)

## チャット入口手順整合

[`default-workflow.md`](../../e2e/default-workflow.md) §0 のプロンプト例どおり:

```
和久桶さん、次の課題をお願いします。

〈依頼内容〉

intake から bootstrap（Asana）→ dispatch（企画チーム）まで進めてください。
```

| step | SKILL / ツール | 現行 doc 参照 |
|------|----------------|---------------|
| intake | workflow-orchestrator | `default-workflow.md` §0 |
| bootstrap | asana-buddy `handoff_to_asana.py` | §1 |
| dispatch | task-dispatcher | §2 |
| planning | planning-pm gate（チャット承認） | §3 · `planning-pm/SKILL.md` |

**prior E2E 証跡（パイプライン本体）:** [`planning-dept-v3-dryrun.md`](../planning/planning-dept-v3-dryrun.md) · [`orchestrator-intake-dryrun.md`](orchestrator-intake-dryrun.md) · [`all-teams-dryrun.md`](../cross-team/all-teams-dryrun.md)

本 dryrun は **移行後の機械検証 + 手順 SSOT 整合** を記録する。フル Asana 実接続 E2E は上記 prior dryrun + 本番チャット依頼で継続する。

## 所見

1. **自動化コア除去完了** — poller / watch / runner / approval_helper / resume_scan は削除。`complete_task.py` から org-os 連動除去。
2. **org-os 本体は参照用残置** — `products/org-os/` · `run_org_os.py doctor` のみ。watch 手順は README から除去済。
3. **回帰 green** — unittest 127/127。`check_milestone_readiness` の subprocess エンコーディングも `errors=replace` で修正。
4. **本番入口はチャットのみ** — Asana タスク作成・遂行（handoff / comment / complete / dispatch）は継続。

## 関連

- 設計: [`chat-driven-ops.md`](../../design/chat-driven-ops.md) · [`workflow-io-contract.md`](../../design/workflow-io-contract.md)
- 廃止設計: [`asana-driven-ops.md`](../../design/asana-driven-ops.md)（RETIRED）
