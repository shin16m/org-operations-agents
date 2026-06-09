# 納品品質 follow-up（M4）— delivery 記録

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-08 |
| 親 Epic | `1215475080199865` |
| ロードマップ M4 トラッカー | `1215475360031077` |
| 参照 | [`delivery-quality-followup-intake.md`](delivery-quality-followup-intake.md) |

## 子タスク完了

| 順 | GID | タイトル | 検証 |
|----|-----|----------|------|
| 1 | `1215475096499996` | pm_intake_gate 拡張 | `test_pm_intake_gate` · smoke `1215475096499996.md` |
| 2 | `1215475097064096` | pm_create_fix_subtask R3 | `test_pm_create_fix_subtask_r3` · `execution_kick_guard.worker_kick_allowed` |
| 3 | `1215475209897115` | pm_emit_worker_prompt fix 注入 | `test_pm_emit_worker_prompt_fix` · dispatch-prompt-ssot §fix コンテキスト |

## smoke dryrun（M4 出口基準）

```powershell
cd E:\data\document\sourse\org-operations-agents
$env:PYTHONIOENCODING='utf-8'
python tools/validate_org_registry.py
python tools/validate_fixture_schemas.py
python tools/validate_ssot_contract.py
python -m unittest tools.test_pm_intake_gate tools.test_pm_create_fix_subtask_r3 tools.test_pm_emit_worker_prompt_fix tools.test_execution_kick_guard -v
```

| コマンド | 結果 |
|----------|------|
| validate_org_registry.py | exit 0 |
| validate_fixture_schemas.py | exit 0 |
| validate_ssot_contract.py | exit 0 |
| unittest（18 tests） | exit 0 |

## SSOT 更新

| パス | 内容 |
|------|------|
| `tools/pm_intake_gate.py` | full/full-ui: AC Must 表 · 実行契約チェック |
| `tools/pm_create_fix_subtask.py` | R3 エスカレーション comment · `fix_escalation: R3` マーカー |
| `tools/execution_kick_guard.py` | `worker_kick_allowed` — R3 時 kick 停止 |
| `tools/pm_emit_worker_prompt.py` | `[fix]` サブ向け review/smoke コンテキスト注入 |
| `docs/design/development-delivery-io.md` | pm_intake_gate 必須節表 |
| `docs/design/dispatch-prompt-ssot.md` | §fix サブ L3b コンテキスト必須 |

## M4 マイルストーン

Epic `1215475080199865` 全子 complete + 上記 smoke dryrun pass → ロードマップ子 `1215475360031077` complete。
