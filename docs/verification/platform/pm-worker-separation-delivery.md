# PM / ワーカー分離ガード — delivery 記録

| 項目 | 内容 |
|------|------|
| 実施 | 2026-06-06 |
| 契機 | watch-auto stuck unblock epic で PM 一括代行 · md 未 attach · 署名見かけ倒し |

## 本体変更

| ファイル | 内容 |
|----------|------|
| `skills/platform/asana-buddy/optional/agent_comment_guard.py` | assignee / skill / attach / signed-comment 検証 |
| `skills/platform/asana-buddy/optional/comment_task.py` | `--skip-assignee-check` · exit 4 |
| `skills/platform/asana-buddy/optional/complete_task.py` | `--skip-worker-guards` · exit 4 |
| `tools/pm_emit_worker_prompt.py` | requirements-writer attach 手順を snippet に追加 |
| `tools/cursor_worker_dispatch.py` | `ORG_OPS_ENFORCE_L3B`（default 1） |
| `tools/execution_resume_scan.py` | `has_agent_comment` を guard に集約 |
| `tools/run_all_teams_dryrun.py` | dryrun は `--skip-worker-guards` |
| `tools/test_agent_comment_guard.py` | unit test |
| `docs/design/pm-worker-separation-enforcement.md` | SSOT |

## 検証

```powershell
python -m unittest tools.test_agent_comment_guard tools.test_execution_resume_scan -v
python tools/validate_ssot_contract.py
python tools/validate_org_registry.py
```

## 期待動作

- PM が worker サブに `--agent product-manager` で comment → **exit 4**
- requirements-writer が attach なしで complete → **exit 4**
- `ORG_OPS_ENFORCE_L3B=1` で API key 無しの `cursor_worker_dispatch -y` → **exit 2**

## 教訓

- ドキュメントだけでは PM 一括完走を止められない — **CLI + L3b kick** が必要
- `comment_task --agent` はラベルではなく **notes 担当: との一致**を機械検証する
