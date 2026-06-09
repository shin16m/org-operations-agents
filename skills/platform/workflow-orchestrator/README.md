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

## intake 三モード

詳細 SSOT: [`docs/design/wakuoke-intake-modes.md`](../../../docs/design/wakuoke-intake-modes.md)

| モード | 用途 |
|--------|------|
| **課題受付**（既定） | 簡単な依頼 → 企画 → Epic 起票 |
| **タスク作成依頼** | タスク化相談 → 合意後 Epic + 子起票 |
| **Epic インプット** | 既存 Epic を dispatch して遂行（intake 省略） |

**マイルストーン:** 各節目で自己評価（組織構築済）。中間は **90 点目標**、最終は **90 点以上必須**。

## 使い方（本番）

### 1. intake — 課題受付（既定）

```
和久桶さん、次の課題をお願いします。

〈依頼内容を自然言語で〉

intake から bootstrap（Asana）→ 企画（Handoff → review → gate）→ execution dispatch まで進めてください。
```

### 2. タスク作成依頼

```
和久桶さん、タスク作成依頼です。〈相談内容〉
Epic 構成とマイルストーン案を提示し、合意後に起票まで進めてください。
```

### 3. Epic インプット（既存 Epic の遂行）

```
和久桶さん、Epic インプットです。親 Epic: 〈URL|GID〉
未完了子を dispatch して遂行を進めてください。
```

### 4. 任意 — Asana タスク URL をチャットで渡す

自動スキャンは行わない。URL を添えて依頼した場合のみ intake-asana として手動読取。

### 5. 企画完了後 — execution 系 dispatch

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
