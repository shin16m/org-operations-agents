# 廃止プロダクト（アーカイブ）

**DEPRECATED · RETIRED（2026-06-09）** — 本番運用から除外。SSOT: [`docs/design/chat-driven-ops.md`](../../docs/design/chat-driven-ops.md)

## org-os

| 項目 | 内容 |
|------|------|
| パス | [`../org-os/`](../org-os/)（**DEPRECATED** · コードは残置） |
| 設計 SSOT | [`docs/design/org-os-product-io.md`](../../docs/design/org-os-product-io.md)（**RETIRED**） |
| 用途（廃止前） | OS State 状態機械 · `watch` · syscall suspend/resume |
| 本番代替 | 和久桶チャット同一セッション · Asana タスク運用（asana-buddy） |

**CLI（非推奨 · 開発・履歴参照のみ）:**

```powershell
python tools/run_org_os.py doctor
```

## 関連ツール（非推奨）

| ツール | 備考 |
|--------|------|
| `tools/run_org_os.py` | org-os CLI ラッパー |
| `tools/complete_epic_os_state.py` | 親 epic OS State=Done（workflow から除外） |
| `tools/sync_org_os_cf_env.py` | CF GID 同期 |

Asana **タスク運用**（`handoff_to_asana` · `comment_task` / `complete_task`）は [`tools/_retired/README.md`](../../tools/_retired/README.md) 参照。
