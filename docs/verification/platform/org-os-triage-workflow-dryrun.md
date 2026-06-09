# org-os triage workflow extension — dryrun 記録

> **履歴（RETIRED · 2026-06-09）** — Asana **自動化** / org-os の検証記録。本番は [chat-driven-ops.md](../../design/chat-driven-ops.md)（和久桶チャット入口 · Asana タスク運用継続）。


| 項目 | 内容 |
|------|------|
| エピック | `1215088809649925` |
| 子タスク | 【2/5】`1215102425337176` |
| 日付 | 2026-05-24 |

## スコープ

- `workflows/default.yaml` v4: **intake → triage → bootstrap → dispatch**
- `tools/intake_triage.py` — snapshot → `epic_input` JSON
- `schemas/platform/epic-input.v1.schema.json`
- `tools/auto_intake_runner.py` — triage 統合（parallel 経路なし）
- `tools/sync_org_os_cf_env.py` — OS State / Approval Required GID 同期
- bootstrap 時 `init_epic_os_state`（`handoff_to_asana.py`）

## コマンド

### CF GID sync

```powershell
python tools/sync_org_os_cf_env.py --project 1214771428861230 --dry-run
```

### triage 単体

```powershell
python tools/intake_triage.py --snapshot output/platform/intake/1215086884850499-snapshot.json
```

### auto-intake E2E（dry-run）

```powershell
python tools/auto_intake_runner.py --task <SOURCE_GID> --dry-run
```

期待出力順: `INTAKE` → `TRIAGE` → `HANDOFF` → `AUTO_BOOTSTRAP dry-run`

### workflow 宣言

```powershell
# workflows/default.yaml version: "4"
# steps: intake, triage, bootstrap, dispatch
```

## 禁止確認

- triage 専用の **別 epic-generator パイプライン** を作っていない
- epic 作成は引き続き **bootstrap / handoff_to_asana** が担う

## 結果

- [x] default.yaml v4
- [x] intake_triage + epic_input schema
- [x] auto_intake_runner triage 統合
- [x] sync_org_os_cf_env.py
- [x] handoff_to_asana init_epic_os_state
