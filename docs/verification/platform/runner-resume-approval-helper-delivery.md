# runner RESUME 前 approval_helper 必須化 — delivery

> **履歴（RETIRED · 2026-06-09）** — Asana **自動化** / org-os の検証記録。本番は [chat-driven-ops.md](../../design/chat-driven-ops.md)（和久桶チャット入口 · Asana タスク運用継続）。


| 項目 | 内容 |
|------|------|
| epic | `1215464614582253` |
| 開発子 | `1215464646737125` |
| intake | `1215437709736921` |

## 変更ファイル

| ファイル | 変更 |
|----------|------|
| `tools/asana_ops_sessions.py` | `approval_sub_gid` 基準の resumable 判定 |
| `tools/asana_ops_poller.py` | `check_session_resume` · RESUME 直前 `run_session_approval_helper` · `_session_auto_kick` 削除 |
| `tools/asana_ops_runner.py` | helper `--parent` = wait_target 優先 |
| `tools/test_runner_approval_helper_order.py` | 回帰 test 新規 |

## 検証

```powershell
python -m unittest tools.test_runner_approval_helper_order tools.test_planning_stuck -v
```

## 運用手順（再現確認）

1. planning gate 【承認】complete（Approval Result=OK 推奨）
2. `python tools/asana_ops_runner.py --once -y --cursor-kick`（または watch-auto）
3. 期待ログ順: `HELPER`/`APPROVED` → `RESUME` → `START` → `DISPATCH`
4. `python tools/org_os.py status --epic <GID>` → `os_state=Running`（kick 後）

## レビュー

| 種別 | 成果物 |
|------|--------|
| requirements | `output/development/requirements/1215464646737125-requirements.md` |
| DocReview | `output/development/reviews/1215464615403934-requirements-review.json` |
| CodeReview | `output/development/reviews/1215464615607386-code-review.json` |
| Verification | `output/development/reviews/1215464888686737-verification.json` |
| spec | `output/development/specs/1215464646737125-spec.md` |
| Mismatch | `output/development/reviews/1215464647795283-mismatch-review.json` |
