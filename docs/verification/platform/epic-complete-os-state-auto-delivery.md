# 親 epic complete → OS State=Done 自動連動 — delivery 記録

| 親 GID | `1215428253771574` |
| 実装サブ | `1215428475113902` |
| 日付 | 2026-06-05 |

## 成果

- `complete_task.py` — Epic 判定（Task Type CF / 親なし+子あり）後、`org-os complete --allow-skip` を Asana 完了マーク直前に実行
- `asana_program_common.py` — `read_task_type` / `is_epic_task`
- `tools/test_complete_task_epic.py` — ユニットテスト
- 要件: `output/development/requirements/1215428253771574-requirements.md`

## 回帰手順

### ユニット

```powershell
python tools/test_complete_task_epic.py
```

### dry-run（org-os のみ · Asana 完了はしない）

```powershell
python tools/org_os.py complete --epic <親GID> --dry-run --allow-skip
```

### E2E（依頼者 · 親 epic が未完了のとき）

1. 親 epic の OS State が Ready / Running / Waiting のいずれかであることを確認
2. `comment_task.py` → `complete_task.py --gid <親GID> -y`
3. Asana で親 epic の **OS State=Done** を確認（CF 未設定時は stderr に WARN · exit 0）

`--strict-os` を付けると org-os 失敗時に exit 1（通常運用は省略）。

## 関連

- 手動 L1 フック: `tools/complete_epic_os_state.py`（orchestrator SKILL 手順）
- 初回 delivery: [`epic-complete-os-done-delivery.md`](epic-complete-os-done-delivery.md)
