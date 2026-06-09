# workflow-orchestrator（和久桶さん）

**課題の入口（本番標準）。** チャットで生課題を受け取り（intake）、bootstrap で Asana に最小タスクを作成し、企画チームへ dispatch する。

利用者向けニックネーム: **和久桶さん**（略: 和久桶）

**運用 SSOT:** [`docs/design/chat-driven-ops.md`](../../../docs/design/chat-driven-ops.md)

詳細: [`SKILL.md`](SKILL.md)

## 用語（認識合わせ）

| 用語 | 意味 |
|------|------|
| **Asana 自動化** | Intake タスク自動検出 · watch · 無人 kick → **廃止** |
| **Asana タスク運用** | `handoff_to_asana` · `comment_task` / `complete_task` 等 → **基本（継続）** |
| **チャット入口** | 和久桶さんへの依頼でエージェントを起動 → **本番標準** |

## 使い方（本番）

### 1. intake — チャットで依頼（ここから開始）

```
和久桶さん、次の課題をお願いします。

〈依頼内容を自然言語で〉

intake から bootstrap（Asana）→ 企画（Handoff → review → gate）→ execution dispatch まで進めてください。
```

### 2. 任意 — Asana タスク URL をチャットで渡す

自動スキャンは行わない。URL を添えて依頼した場合のみ intake-asana として手動読取。

### 3. 企画完了後 — execution 系 dispatch

企画チームから `DeptWorkComplete` を受け取ったら、未完了の execution 系子を task-dispatcher で順次配賦する。

### 4. Asana 同期（基本）

各チーム PM が `comment_task.py` → `complete_task.py -y` を実行。全子完了後に親エピックも完了。

## 使わないもの（Asana 自動化 · 廃止）

- `org-ops-watch` · `asana_ops_poller` · org-os watch
- `--record-wait` · approval_helper 常駐

## workflow の選び方

| 目的 | ファイル |
|------|----------|
| 標準（企画 dispatch まで） | [`workflows/default.yaml`](../../../workflows/default.yaml) v6 |
| + execution 系 dispatch ループ | [`workflows/with-dispatch.yaml`](../../../workflows/with-dispatch.yaml) |
| 企画チーム L3 | [`workflows/planning-delivery.yaml`](../../../workflows/planning-delivery.yaml) |

## 参照

- E2E: [`docs/e2e/default-workflow.md`](../../../docs/e2e/default-workflow.md)
- I/O: [`docs/design/workflow-session-io.md`](../../../docs/design/workflow-session-io.md)
