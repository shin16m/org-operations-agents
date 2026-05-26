# org-os

組織OS — epic 単位の **Ready / Running / Waiting / Done** 状態機械（外部プロダクト）。

org-operations-agents 本体は **CLI 契約経由**で本パッケージを呼び出す。状態機械本体・Asana CF read/write はここに集約する。

## 前提

- Asana プロジェクトに **OS State** · **OS Suspend Reason** · **Approval Required** CF が存在すること（依頼者が追加）
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
org-os dispatch --epic <PARENT_GID> [--dry-run]   # alias: syscall start (ORG_OS_AGENT_ID required)
org-os complete --epic <PARENT_GID> [--dry-run] [--allow-skip]
org-os queue ready --project <PROJECT_GID> [--json]
org-os queue wait --project <PROJECT_GID> [--json]
org-os syscall start|suspend|resume|complete --epic <GID> ...
org-os watch --project <PROJECT_GID> [--interval 60] [--once]
```

Suspend reason values use **Asana enum display names**: `Approval`, `Human Review`, `External Block` (not snake_case).

`complete` は **Ready / Running / Waiting** から **Done** へ遷移（bootstrap 直後 Ready の epic も対象）。L1 では `tools/complete_epic_os_state.py`（デフォルト `--allow-skip`）を `comment_epic_summary` 後に実行。

`watch` / `queue` は **Agent Type=AI** かつ **Task Type=Epic** のタスクのみ走査する。

### 状態遷移

```
Ready --(start)--> Running
Ready/Running --(suspend)--> Waiting  (+ OS Suspend Reason)
Waiting --(resume)--> Ready
Ready/Running/Waiting --(complete)--> Done
```

`start` は **Ready** epic のみ **Running** へ遷移する（org-ops dispatch 起動前の OS 側フック想定）。
