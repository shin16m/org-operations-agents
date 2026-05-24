# org-os

組織OS — epic 単位の **Ready / Running / Waiting / Done** 状態機械（外部プロダクト）。

org-operations-agents 本体は **CLI 契約経由**で本パッケージを呼び出す。状態機械本体・Asana CF read/write はここに集約する。

## 前提

- Asana プロジェクトに **OS State** · **Approval Required** CF が存在すること（依頼者が追加）
- GID は org-ops 側で同期:

```powershell
python tools/sync_org_os_cf_env.py --project <PROJECT_GID> --dry-run
python tools/sync_org_os_cf_env.py --project <PROJECT_GID> --write -y
```

`.env` は `skills/platform/asana-buddy/optional/.env` を `ORG_OS_ENV_FILE` で上書き可能。

## インストール（開発）

```powershell
cd products/org-os
pip install -e .
```

## CLI

```powershell
org-os status --epic <PARENT_GID>
org-os dispatch --epic <PARENT_GID> [--dry-run]
org-os watch --project <PROJECT_GID> [--interval 60] [--once]
```

### 状態遷移

```
Ready --(dispatch)--> Running
Running --(need_approval)--> Waiting
Waiting --(approval_done)--> Ready
Running --(complete)--> Done
```

`dispatch` は **Ready** epic のみ **Running** へ遷移する（org-ops task-dispatcher 起動前の OS 側フック想定）。
