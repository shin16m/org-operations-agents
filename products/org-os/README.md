# org-os

> **DEPRECATED · RETIRED（2026-06-09）** — org-os 状態機械・watch 連携は本番運用から除外。標準は [`docs/design/chat-driven-ops.md`](../../docs/design/chat-driven-ops.md)。アーカイブ索引: [`products/_retired/README.md`](../_retired/README.md)

組織OS — epic 単位の **Ready / Running / Waiting / Done** 状態機械（外部プロダクト · **参照用にコード残置**）。

org-operations-agents 本体は **CLI 契約経由**で本パッケージを呼び出す。状態機械本体・Asana CF read/write はここに集約する。

**外部利用（リポジトリ外）:** [`CONSUMER.md`](CONSUMER.md) · **リリース手順:** [`RELEASE.md`](RELEASE.md) · 版 **1.0.0**

## 初回セットアップ（doctor のみ · watch 不要）

詳細手順: [`docs/e2e/org-os-first-setup.md`](../../docs/e2e/org-os-first-setup.md)（**履歴参照** — 本番では org-os セットアップ不要）

```powershell
# リポジトリルートで（venv · .env · doctor · sync 案内を一括）
.\scripts\org-ops\setup.ps1

# 検証（ローカル env → Asana 実接続）
.\.venv\Scripts\python.exe .\tools\run_org_os.py doctor
.\.venv\Scripts\python.exe .\tools\run_org_os.py doctor --online
```

1. **token（手動）** — `skills/platform/asana-buddy/optional/.env` に `ASANA_TOKEN` を設定
2. **setup.ps1** — venv 作成 · `.env` 初期化 · `doctor` 実行
3. **doctor** — 不足キーがあれば stderr に `FIX` / `NEXT` を表示
4. **sync** — CF GID 不足時は `sync_*_env.py --write -y`（`setup.ps1 -Sync` でも可）
5. **doctor --online** — プロジェクトと CF enum 名を API 照合

~~6. **watch --once**~~ — **廃止**（Asana 自動化 / org-os watch は本番から除外）

`.env` は `skills/platform/asana-buddy/optional/.env` を `ORG_OS_ENV_FILE` で上書き可能。

## 前提（Asana 側）

- プロジェクトに **OS State** · **OS Suspend Reason** · **Approval Required** · **Agent Type** · **Task Type** CF が存在すること
- GID は `doctor` → sync CLI で `.env` に反映（手動編集は非推奨）

## インストール

### 単体（org-ops リポジトリ外 · v1.0.0）

```powershell
cd products/org-os
pip install -e .
org-os doctor
org-os queue ready --project <PROJECT_GID> --json
```

`pip install -e .` 後は **sys.path 不要**。`ASANA_TOKEN` と CF GID は `.env` または環境変数で渡す（`ORG_OS_ENV_FILE` でパス指定可）。

### モノレポ開発（org-operations-agents 内）

```powershell
cd products/org-os
pip install -e ".[dev]"    # org-os CLI + pytest
pytest tests -q
```

リポジトリルートからは **ラッパー** を使える（`tools/` が sys.path 先頭でも package shadow を回避）:

```powershell
python tools/run_org_os.py doctor
```

`pip install -e .` 済みなら `org-os doctor` でも可（ラッパーと同じ CLI）。

## CLI

| 入口 | 用途 |
|------|------|
| `org-os <command>` | pip install 後の正規エントリポイント |
| `python tools/run_org_os.py <command>` | モノレポ内ラッパー（install 済みなら同じ `org_os.cli`） |

```powershell
org-os doctor [--online]                              # 初回セットアップ検証（local / API）
org-os status --epic <PARENT_GID>
org-os dispatch --epic <PARENT_GID> [--dry-run]   # alias: syscall start (ORG_OS_AGENT_ID required)
org-os complete --epic <PARENT_GID> [--dry-run] [--allow-skip]
org-os queue ready --project <PROJECT_GID> [--json]
org-os queue wait --project <PROJECT_GID> [--json]
org-os syscall start|suspend|resume|complete --epic <GID> ...
org-os watch --project <PROJECT_GID> [--interval 60] [--once]   # RETIRED — 本番では使用しない
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
