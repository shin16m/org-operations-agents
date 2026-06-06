# org-os 外部プロダクト — dryrun 記録

| 項目 | 内容 |
|------|------|
| エピック | `1215088809649925` |
| 子タスク | 【3/5】`1215088624074728` |
| プロダクト | `products/org-os/` |
| 日付 | 2026-05-24 |

## 前提

- 依頼者が Asana プロジェクト `1214771428861230` に **OS State** · **Approval Required** CF を追加済み
- GID sync:

```powershell
python tools/sync_org_os_cf_env.py --project 1214771428861230 --dry-run
python tools/sync_org_os_cf_env.py --project 1214771428861230 --write -y
```

## インストール（任意）

```powershell
cd products/org-os
pip install -e .
org-os status --epic 1215088809649925
```

## リポジトリルート wrapper（pip 不要）

```powershell
python tools/org_os.py status --epic 1215088809649925
python tools/org_os.py dispatch --epic 1215088809649925 --dry-run
python tools/org_os.py watch --project 1214771428861230 --once
```

## 状態遷移

```
Ready --(dispatch)--> Running
Running --(need_approval)--> Waiting
Waiting --(approval_done)--> Ready
Running --(complete)--> Done
```

## org-ops との境界

| 側 | 責務 |
|----|------|
| org-ops | intake → triage → bootstrap · `.env` GID sync · `init_epic_os_state` on create |
| org-os | epic CF read/write · dispatch/watch CLI · 状態機械本体 |

詳細 SSOT は governance 子【4/5】で `docs/design/org-os-product-io.md` として整備予定。

## 結果

- [x] `products/org-os/` パッケージ scaffold
- [x] CLI: `status` · `dispatch` · `watch`
- [x] `tools/org_os.py` wrapper
- [x] README + pyproject.toml
