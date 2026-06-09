# チャットドリブン運用 — org-ops SSOT

| 版 | 1.2 |
| 日付 | 2026-06-09 |
| 状態 | **本番標準** |
| SSOT id | `chat-driven-ops` |

## 目的

**token コスト制約**のため、Asana 上のタスクを**自動検出してエージェントを起動する機能**（本ドキュメントでは **Asana 自動化** と呼ぶ）を棄却した。

一方で、**Asana タスクの作成と遂行**（`handoff_to_asana` · `pm_assign_subtasks` · `comment_task` / `complete_task` 等）はこれまで通り **基本** とする。

## 用語の定義（認識合わせ）

| 用語 | 意味 | 本番 |
|------|------|------|
| **Asana 自動化** | Intake タスク等の**自動検出** · ポーリング · watch 常駐 · 自動 kick · org-os watch · `--record-wait` 再開ループ | **廃止・削除** |
| **Asana タスク運用** | 和久桶セッション内で Handoff を Asana に投入し、子タスクを**作成・遂行・完了**する一連の操作（asana-buddy） | **基本（継続）** |
| **チャット入口** | 依頼者が **和久桶さん** に自然言語で依頼し、エージェント起動のトリガーとする | **本番標準** |

**整理:**

- 「Asana をやめる」のではない → **自動検出・無人起動だけやめる**
- 「Asana タスクを作って遂行する」は変わらない → 和久桶さんへの**チャット依頼**から同一セッションで実行する

## 標準入口（本番）

| 用途 | 入口 | 備考 |
|------|------|------|
| **本番依頼** | Cursor チャットで **和久桶さん** に自然言語で依頼 | エージェント起動のトリガー |
| **タスク作成依頼** | 「タスク化の相談」等で和久桶に相談 | `task_creation_request` — 合意後 Epic 起票 |
| **Epic インプット** | 既存 Epic の URL/GID を渡して遂行再開 | `epic_input` — intake/bootstrap 省略 |
| Asana タスク URL 渡し | チャット内で URL/GID を添えて依頼 | **手動** intake-asana（自動スキャンなし） |
| bootstrap / asana_execute | 和久桶セッション内で `handoff_to_asana.py` | **基本** — Asana 親 + 子の作成・更新 |
| 子タスク遂行 | 各 PM / worker が Asana 子を消化 | `comment_task` → `complete_task`（署名付き） |

intake 三モードの詳細: [`wakuoke-intake-modes.md`](wakuoke-intake-modes.md)

## 廃止するもの（Asana 自動化）

| 対象 | 内容 |
|------|------|
| [`asana-driven-ops.md`](asana-driven-ops.md) | ポーリング · watch · auto-intake · RESUME ダッシュボード |
| [`org-os-product-io.md`](org-os-product-io.md) | OS State 状態機械 · `org-os watch` · syscall suspend/resume |
| `scripts/org-ops/org-ops-watch*` | 常駐 runner |
| `asana_ops_poller` / `asana_ops_runner` | Intake タスク自動検出 · 自動 kick |
| `--record-wait` / `approval_helper` 常駐 | バックグラウンド再開ループ |

## 継続するもの（Asana タスク運用）

| 操作 | スクリプト / スキル |
|------|---------------------|
| bootstrap 投入 | `handoff_to_asana.py`（bootstrap Handoff） |
| 本番 Handoff 投入 | `handoff_to_asana.py --require-review-result` |
| 子タスク分解 | `pm_assign_subtasks.py` |
| 作業コメント・完了 | `comment_task.py` → `complete_task.py` |
| dispatch | `task_dispatcher.py`（Asana 子 GID ベース） |
| エピック完了 | `comment_epic_summary.py` → 親 `complete_task.py` |

## 標準パイプライン

```
依頼者 ──チャット──► 和久桶さん（workflow-orchestrator）
                         intake（自然言語）
                           → bootstrap Handoff → handoff_to_asana（Asana 親 + 企画子）
                           → dispatch → planning-pm
                               → issue-story-planner → plan-reviewer（必須）
                               → planning-pm（gate）→ handoff_to_asana（実行系子）
                           → task-dispatcher → 各 PM L3
                               → pm_assign_subtasks → workers
                               → comment_task → complete_task（各子）
```

パイプライン詳細: [`workflow-io-contract.md`](workflow-io-contract.md)

## 和久桶さんへの依頼文（テンプレ）

```
和久桶さん、次の課題をお願いします。

〈自然言語で依頼内容〉

intake から bootstrap → 企画（Handoff → review → gate）→ Asana 投入 → execution 系 dispatch まで進めてください。
```

## ゲート（チャット前提）

| ゲート | デフォルト | 備考 |
|--------|------------|------|
| **planning gate** | Handoff 要約提示後 **同一セッションで `asana_execute`** | チャット「すすめて」で有効 |
| **L2 execution dispatch** | 企画完了後 **自動進行**（確認なし） | [`dispatch-auto-proceed-ssot.md`](dispatch-auto-proceed-ssot.md) |
| **PM review gate** | **省略**（opt-in のみ） | `human_review_gate` 等 |

opt-in 人間承認は**チャットで確認**。`--record-wait` · org-os Waiting は使わない。

## 例外

利用者が **「Asana 不要」「workflow 省略」** と明示した場合のみ、Handoff JSON と `output/` 成果物のみで完結可（[`workflow-intake-required.mdc`](../../.cursor/rules/workflow-intake-required.mdc)）。

## セッション I/O

- 状態: [`workflow-session-io.md`](workflow-session-io.md) · `intake_mode: natural_language`（既定）
- Asana GID: `parent_gid` · `planning_child_gid` をセッションに記録
- **SuspendedSession / `--record-wait` は使用しない**

## 関連（廃止ドキュメント）

| 旧 SSOT | 状態 |
|---------|------|
| [`asana-driven-ops.md`](asana-driven-ops.md) | **RETIRED**（Asana 自動化の履歴） |
| [`org-os-product-io.md`](org-os-product-io.md) | **DEPRECATED · RETIRED** |
| [`products/_retired/README.md`](../../products/_retired/README.md) | org-os アーカイブ索引 |
| [`docs/e2e/org-ops-watch-runbook.md`](../e2e/org-ops-watch-runbook.md) | **RETIRED** |

## 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-06-09 | v1.0 — Asana 自動化棄却 · チャット入口を本番標準に固定 |
| 2026-06-09 | v1.1 — 用語定義追加。Asana タスク運用は基本として明記 |
| 2026-06-09 | v1.2 — intake 三モード（[`wakuoke-intake-modes.md`](wakuoke-intake-modes.md)）参照追加 |
