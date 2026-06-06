# Asana PM 運用強化 — dryrun 記録

| 日付 | 2026-05-24 |
| エピック | `1215086341081688` |
| ベースライン | `1dcd40a` |

## F1: review gate dependencies

| 項目 | 結果 |
|------|------|
| `add_task_dependencies` | `asana_program_common.py` に追加 |
| `wire_worker_subs_to_review_gate` | `create_pm_review_gate.py` から自動実行 |
| `pm_emit_worker_prompt` gate 未達 | `check_pm_review_gate` 非 0 → exit 1 |
| Asana UI | review 未 complete 時 worker サブが gate に依存（要実機確認） |

## F2: worker サブ CF

| 項目 | 結果 |
|------|------|
| `pm_assign_subtasks` | 各 worker サブ作成後 `set_assignee_type_org_ops`（PUT のみ） |
| 成功/失敗 | CLI 出力 `CF=AI` / `CF=skip` · 400 時 stderr 警告 |
| layout-fix | `addProject` 不使用 |

## F3: validate 強化

| 項目 | 結果 |
|------|------|
| `validate_ssot_contract.py` | 5 PM assignment doc に `create_pm_review_gate` + `人間` 必須 |
| dependencies SSOT | `addDependencies` 文言を pm-assign / planning-gate doc に追記 |

## F4: gate 整理

| 項目 | 結果 |
|------|------|
| `docs/design/planning-gate-vs-pm-review-gate.md` | 新規 |
| `workflow-io-contract.md` | 相互リンク |

## 検証コマンド

```powershell
python tools/validate_ssot_contract.py
python tools/validate_org_registry.py
python skills/platform/asana-buddy/optional/pm_assign_subtasks.py --help
python tools/create_pm_review_gate.py --help
python tools/check_pm_review_gate.py --parent <PM子GID>
python tools/pm_emit_worker_prompt.py --parent <PM子GID> --department governance
```

## 運用上の注意

- 【レビュー】/【承認】サブは **人間が Asana UI で complete**（エージェント `complete_task` 禁止）
- チャット「すすめて」は planning gate のみ。PM review gate は Asana complete 必須
