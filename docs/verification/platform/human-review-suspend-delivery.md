# Human Review suspend — delivery

| 項目 | 内容 |
|------|------|
| エピック | `1215133615586405` |
| 日付 | 2026-05-26 |

## 概要

PM review gate 待ち時、`--record-wait` / `create_approval_subtask` が **親 epic** を org-os `Waiting` + `Human Review` に suspend。`approval_helper` は epic を resume。

## 変更

| ファイル | 内容 |
|---------|------|
| `products/org-os/src/org_os/asana_client.py` | `resolve_epic_gid` |
| `skills/.../create_approval_subtask.py` | epic 解決 · PM 子→`Human Review` |
| `tools/approval_helper.py` | epic resume · log `parent_gid`=epic |
| `tools/asana_ops_poller.py` | `--record-wait` pm_review → epic suspend · session `epic_gid` |
| `docs/design/planning-gate-vs-pm-review-gate.md` | org-os 表 |

## 検証

```powershell
python tools/org_os.py status --epic <親GID>
# PM review record-wait 後: Waiting · Human Review
python tools/org_os.py queue wait --project 1214771428861230 --json
```

## 関連

- Handoff: `output/planning/handoff/handoff.human-review-suspend.json`
