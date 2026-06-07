# org-os 初回セットアップ（約 10 分）

epic 状態機械（org-os）を使い始めるまでの最短手順。SSOT: [`products/org-os/README.md`](../../products/org-os/README.md)

## 前提

- Windows + PowerShell
- Python 3.10+（`python` が PATH にあること）
- Asana Personal Access Token（[My Apps](https://app.asana.com/0/my-apps) で発行）

## 1. リポジトリを clone 済みであること

```powershell
cd <org-operations-agents ルート>
```

## 2. 一括セットアップ（推奨）

```powershell
.\scripts\org-ops\setup.ps1
```

| ステップ | 内容 |
|----------|------|
| 1 | `setup_venv` — ルート `.venv` 作成 |
| 2 | `.env` 確認 — なければ `.env.example` からコピー |
| 3 | `doctor` — 必須 env キー検証 |
| 4 | sync 案内 — CF GID 不足時に次コマンドを表示 |

**手動（token）:** `skills/platform/asana-buddy/optional/.env` に `ASANA_TOKEN` を設定（自動化対象外）。

**CF 自動同期（任意）:**

```powershell
.\scripts\org-ops\setup.ps1 -SkipVenv -Sync
```

## 3. doctor で検証

```powershell
.\.venv\Scripts\python.exe .\tools\org_os.py doctor
.\.venv\Scripts\python.exe .\tools\org_os.py doctor --online
```

- `doctor` — ローカル `.env` の必須キー 15 件
- `doctor --online` — Asana プロジェクト + CF enum 名の SSOT 照合

いずれも `PASS` なら org-os CLI が使える状態。

## 4. watch で動作確認

```powershell
.\.venv\Scripts\python.exe .\tools\org_os.py watch --project <ASANA_PROJECT_ID> --once
```

Ready / Waiting の epic 一覧が表示されれば完了。

## トラブルシュート

| 症状 | 対処 |
|------|------|
| `MISSING ASANA_TOKEN` | `.env` に token を設定 |
| CF GID 不足（まとめて） | `python tools/sync_all_cf_env.py --project <GID> --write -y` |
| legacy Epic（OS State なし） | `python tools/backfill_epic_os_state.py --project <GID> --dry-run` |
| online ERROR（enum 不一致） | 上記 sync を再実行し `doctor --online` を再試行 |

## 関連

- org-os プロダクト README: [`products/org-os/README.md`](../../products/org-os/README.md)
- org-ops デフォルト workflow: [`default-workflow.md`](default-workflow.md)
