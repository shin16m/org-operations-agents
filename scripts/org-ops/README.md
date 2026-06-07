# org-ops バッチスクリプト

Windows 向け運用エントリ。venv · `PYTHONIOENCODING` は [`_common.ps1`](_common.ps1) / [`_common.cmd`](_common.cmd) で共通化。

## 本番標準（watch 常駐）

| スクリプト | 用途 |
|------------|------|
| [`org-ops-watch.ps1`](org-ops-watch.ps1) | **本番標準** — `asana_ops_runner --watch` |
| `org-ops-watch.cmd` | 上記（ヒントのみ · `-y` なし） |
| `org-ops-watch-yes.cmd` | 本番 watch（`-Yes` · bootstrap 実行） |
| `org-ops-watch-auto.cmd` | 本番 + AutoKick（要 `CURSOR_API_KEY`） |

```powershell
# 初回セットアップ後
.\scripts\org-ops\setup.ps1 -SkipVenv

# 本番 watch（snippet-only）
.\scripts\org-ops\org-ops-watch.ps1 -Yes -Human

# watch + dashboard 同時起動
.\scripts\org-ops\org-ops-watch.ps1 -Yes -Human -Dashboard

# 黒窓なしバックグラウンド watch（stdout+stderr 統合: output/platform/runner-watch.log）
.\scripts\org-ops\org-ops-watch.ps1 -Yes -AutoKick -Background -Dashboard

# 停止（runner + dashboard）
.\scripts\org-ops\org-ops-stop.ps1

# ダッシュボード単体（接続拒否時はこちらを先に起動）
.\scripts\org-ops\org-ops-dashboard.ps1
# フォアグラウンド（エラー確認用）
.\scripts\org-ops\org-ops-dashboard.ps1 -Foreground

# AutoKick
$env:CURSOR_API_KEY = "<key>"
.\scripts\org-ops\org-ops-watch.ps1 -Yes -AutoKick -Interval 60
```

## 初回セットアップ

| スクリプト | 用途 |
|------------|------|
| [`setup.ps1`](setup.ps1) | venv · .env · doctor · sync 案内 |
| `setup.cmd` | 上記（cmd ラッパー） |

## 検証・開発

| スクリプト | 用途 |
|------------|------|
| [`org-ops-once-dryrun.ps1`](org-ops-once-dryrun.ps1) | 1 サイクル dry-run |
| `org-ops-once-dryrun.cmd` | 上記 |
| [`org-ops-start.cmd`](org-ops-start.cmd) | メニュー起動（リポジトリ直下にも symlink 可） |
| `org-ops-dispatch.cmd` | 人手 `task_dispatcher`（fallback） |
| `org-ops-webhook.cmd` | Webhook 常駐 |

## Windows 常駐（Task Scheduler 例）

1. **プログラム:** `powershell.exe`
2. **引数:** `-NoProfile -ExecutionPolicy Bypass -File "E:\path\to\org-operations-agents\scripts\org-ops\org-ops-watch.ps1" -Yes -Interval 60`
3. **開始:** リポジトリルート（または `ORG_OPS_REPO_ROOT` を環境変数に設定）
4. **条件:** ネットワーク接続時のみ（任意）

# AutoKick 版は `org-ops-watch-auto.cmd` をタスクに登録（`.env` の `CURSOR_API_KEY` / `ORG_OPS_AUTO_KICK` を使用。PowerShell は `Import-OrgOpsDotEnv` で同 .env を読む）

## 開発常駐（手動）

```powershell
cd <repo-root>
.\scripts\org-ops\org-ops-watch.ps1 -Yes -Human -Interval 30
```

`Ctrl+C` で停止。ログは標準出力をファイルリダイレクト:

```powershell
.\scripts\org-ops\org-ops-watch.ps1 -Yes 2>&1 | Tee-Object -FilePath .\output\platform\runner-watch.log
```

## 関連ドキュメント

- 運用 runbook: [`docs/e2e/org-ops-watch-runbook.md`](../../docs/e2e/org-ops-watch-runbook.md)
- SSOT: [`docs/design/asana-driven-ops.md`](../../docs/design/asana-driven-ops.md)
- 初回セットアップ: [`docs/e2e/org-os-first-setup.md`](../../docs/e2e/org-os-first-setup.md)
