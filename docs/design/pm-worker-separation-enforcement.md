# PM / ワーカー分離 — 実行時ガード

| 版 | 1.0 |
| 日付 | 2026-06-06 |
| 背景 | PM 一括セッションによる worker 代行 · 署名見かけ倒し · md 未 attach |

## 目的

1. **PM は自分の業務外（ワーカー成果物）に手を出さない**
2. **comment の `agent` / `skill` は notes `担当:` と一致**（実作業ワーカーのみ署名）
3. **requirements-writer / dev-reviewer** の md attach を complete 前に強制

設計 SSOT: [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md) · [`development-pm-assignment.md`](development-pm-assignment.md)

## CLI ガード

| ツール | 検証 | 回避（dryrun のみ） |
|--------|------|---------------------|
| `comment_task.py` | `--agent` == notes `担当:` · `--skill` == registry SKILL.md · PM slug は PM 担当タスクのみ | `--skip-assignee-check` |
| `complete_task.py` | ワーカー subs: 署名 comment 必須 · rw/dev-reviewer: md attach | `--skip-worker-guards` |

実装: [`skills/platform/asana-buddy/optional/agent_comment_guard.py`](../../skills/platform/asana-buddy/optional/agent_comment_guard.py)

### exit code

| code | 意味 |
|------|------|
| 4 | assignee / attach / signed-comment ガード違反 |

## L3b 強制

| 環境変数 | 既定 | 内容 |
|----------|------|------|
| `ORG_OPS_ENFORCE_L3B` | `1` | `cursor_worker_dispatch.py -y` で `CURSOR_API_KEY` 未設定時 **exit 2**（手動完走を抑止） |
| `ORG_OPS_ENFORCE_L3B=0` | — | SKIP exit 0 + `pm_emit_worker_prompt` 手動 |

和久桶セッションまたは PM dispatch から `cursor_worker_dispatch` でワーカーは **別セッション** kick（**Asana 自動化 runner 廃止** · [`chat-driven-ops.md`](chat-driven-ops.md)）。

## 正規フロー（再掲）

```
PM intake → pm_assign_subtasks → check_pm_review_gate
  → pm_emit_worker_prompt（1 サブのみ）
  → cursor_worker_dispatch（別セッション）
  → worker: 成果物 + attach + comment_task
  → pm_worker_complete_bridge（PM が当該サブ complete のみ）
  → 次サブへ繰り返し
```

**禁止:** 同一セッションで複数 worker の成果物を書き、ループで `comment_task` / `complete_task` する。

## 事後補完（Plan B）

[`asana-comment-detail-delivery.md`](../verification/platform/asana-comment-detail-delivery.md) 型の **監査証跡事後スタンプ** は、利用者が **「workflow 省略」** と明示した場合のみ。通常 epic では CLI ガードにより **一括 stamp は失敗**する。

## 関連

- delivery: [`pm-worker-separation-delivery.md`](../verification/platform/pm-worker-separation-delivery.md)
- attach: [`development-delivery-io.md`](development-delivery-io.md)
- 署名: [`agent-asana-comment-signature.md`](agent-asana-comment-signature.md) §8
