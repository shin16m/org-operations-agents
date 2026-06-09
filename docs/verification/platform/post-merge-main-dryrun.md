# post-merge main — dryrun 記録

> **履歴（RETIRED · 2026-06-09）** — Asana **自動化** / org-os の検証記録。本番は [chat-driven-ops.md](../../design/chat-driven-ops.md)（和久桶チャット入口 · Asana タスク運用継続）。


| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-04 |
| ブランチ | `main` @ merge `8662864` |
| epic | `1215414654038443` |

## 検証コマンド

```powershell
python tools/validate_org_registry.py
python tools/validate_fixture_schemas.py
python tools/validate_ssot_contract.py
python tools/check_new_department.py --all
python tools/asana_ops_poller.py --once --project 1214771428861230 --dry-run --human
```

## 期待

- bootstrap 直後: `PLANNING_DISPATCH`（`DISPATCH` なし）
- planning gate RESUME 後: `DISPATCH phase=execution`

## 結果

| 段階 | 確認 | 結果 |
|------|------|------|
| validate 4 本（main） | 2026-06-04 | **OK** |
| bootstrap 直後 | `PLANNING_DISPATCH` · `DISPATCH` なし | **OK**（epic `1215414654038443`） |
| planning gate RESUME | `wakuoke_resume_scan` → `RESUME result=OK` | **OK** |
| 企画子未完了時 | 再スキャンで `PLANNING_DISPATCH`（execution 抑制） | **OK** |
| `handoff_to_asana` | 開発子 `1215414654592197` 作成 | **OK** |

## epic

- 親: `1215414654038443`
- 企画子: `1215423732603339`
- 開発子: `1215414654592197`
