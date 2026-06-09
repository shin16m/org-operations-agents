# org-os — 外部利用ガイド（CONSUMER）

> **DEPRECATED（2026-06-09）** — 本番運用から除外。履歴参照のみ · [`products/_retired/README.md`](../_retired/README.md)

org-operations-agents リポジトリ外から **org-os** を syscall / queue 経由で使う最小手順（**非推奨**）。

SSOT: [`docs/design/org-os-product-io.md`](../../docs/design/org-os-product-io.md) · 版 **1.0.0**

## 1. インストール

```powershell
git clone <org-operations-agents-url>
cd org-operations-agents/products/org-os
pip install -e .
```

`org-os --help` が表示されれば OK。`requests` のみ必須依存。

## 2. 環境変数（`.env`）

`skills/platform/asana-buddy/optional/.env` をコピーするか、次を最低限設定:

| キー | 用途 |
|------|------|
| `ASANA_TOKEN` | Asana PAT |
| `ASANA_PROJECT_ID` | 監視プロジェクト GID |
| `ORG_OS_AGENT_ID` | `syscall.start` 用（例: `workflow-orchestrator`） |
| `ASANA_OS_STATE_*` | OS State CF + enum GID（sync CLI で取得） |

```powershell
# モノレポ clone 時のみ — CF GID を .env に書き込み
python tools/sync_org_os_cf_env.py --project <PROJECT_GID> --write -y
```

`ORG_OS_ENV_FILE` で `.env` パスを上書き可能。

## 3. doctor（初回検証）

```powershell
org-os doctor
org-os doctor --online
```

ローカル env 不足は `FIX` / `NEXT` 行で修復コマンドが出る。

## 4. syscall（write path）

**禁止:** epic の OS State を Asana API で直接 PUT しない。必ず syscall 経由。

```python
from org_os import syscall

# bootstrap 後
syscall.init_epic("EPIC_GID")

# dispatch 起動前
syscall.start("EPIC_GID")  # ORG_OS_AGENT_ID 必須

# 人間 gate 待ち
syscall.suspend("EPIC_GID", "Approval", ref="APPROVAL_SUB_GID")

# 承認完了後
syscall.resume("EPIC_GID", ref="APPROVAL_SUB_GID")

# エピック完走
syscall.complete("EPIC_GID")
```

CLI  equivalent:

```powershell
org-os syscall start --epic <GID>
org-os syscall suspend --epic <GID> --reason Approval --ref <SUB>
org-os syscall resume --epic <GID>
org-os complete --epic <GID>
```

Suspend reason は Asana 表示名のみ: `Approval` · `Human Review` · `External Block`

## 5. queue（read-only）

```python
from org_os.queue import ready_queue, wait_list

ready = ready_queue("PROJECT_GID")
waiting = wait_list("PROJECT_GID")
```

```powershell
org-os queue ready --project <PROJECT_GID> --json
org-os queue wait --project <PROJECT_GID> --json
org-os watch --project <PROJECT_GID> --once
```

フィルタ: **Agent Type=AI** · **Task Type=Epic** · `ready_queue` は Approval Required≠Yes。

## 6. モノレポ内ラッパー

org-operations-agents 開発時は `python tools/org_os.py` でも同じ CLI（[`tools/org_os.py`](../../tools/org_os.py)）。外部配布時は `org-os` コマンドを正とする。

## 7. 関連

- 初回セットアップ: [`docs/e2e/org-os-first-setup.md`](../../docs/e2e/org-os-first-setup.md)
- リリース: [`RELEASE.md`](RELEASE.md)
- semver: `org-os-product-io.md` §10
