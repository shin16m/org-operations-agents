# planning gate と PM review gate — 整理 SSOT

| 版 | 1.7 |
| 日付 | 2026-06-09 |
| 本番 SSOT | [`chat-driven-ops.md`](chat-driven-ops.md) |

## 3 種類のゲート（人間 / 自動）

| ゲート | 段階 | 担当 | 対象 | デフォルト | opt-in |
|--------|------|------|------|------------|--------|
| **planning gate** (`handoff_approved`) | L3 企画 | planning-pm | Handoff 要約 · execution 系子 Asana 投入 | 要約提示後 **同一セッションで** `handoff_to_asana.py` | チャットで依頼者へ明示確認 |
| **L2 execution dispatch** | L1/L2 · `asana_execute` 後 | workflow-orchestrator | 未完了 execution 系子 → task-dispatcher → PM | **自動進行**（チャット確認しない） | `human_execution_dispatch` · `ORG_OPS_EXECUTION_DISPATCH_CONFIRM=1`（[`dispatch-auto-proceed-ssot.md`](dispatch-auto-proceed-ssot.md)） |
| **PM review gate** (`pm_review_gate`) | L3 各 PM | product-manager / ux-pm / … | worker サブ構成・担当 slug | **gate 省略** | `create_pm_review_gate.py` · `human_review_gate` |

## 混同しやすい点

- **planning gate の「承認」** = execution 系子タスクを Asana に**作ってよい**（実装開始の合図**ではない**）。
- **L2 execution dispatch** = 投入済み execution 系子を **task-dispatcher → PM** へ配賦。**デフォルトはチャット確認なし**。
- **PM review gate の「完了」** = 当該 PM 子の **L3b worker dispatch 可**。**デフォルトでは gate 自体を作らない**。
- チャットの「すすめて」「承認」は **planning gate · L2 dispatch デフォルト（opt-out）** で有効。

## F1: Asana dependencies

`create_pm_review_gate.py` 実行後、各 worker サブは【レビュー】サブに **Asana dependency** を付与する（`addDependencies`）。  
人間が review サブを complete するまで worker サブは Asana 上もブロックされる。

## planning gate デフォルト（opt-out · 本番）

`PlanReviewResult` 通過後:

1. planning-pm: Handoff 要約を提示
2. **同一セッションで** `handoff_to_asana.py --require-review-result` を実行
3. 【承認】サブ・`--record-wait` · `approval_helper` 常駐は **使わない**

## planning gate opt-in（評価・監査）

トリガー（いずれか）:

- `create_planning_approval_gate.py --require-human-approval`
- Handoff `meta.human_planning_approval: true`
- env `ORG_OPS_PLANNING_APPROVAL_GATE=1`
- epic notes `human_planning_approval: yes`

1. planning-pm: `create_planning_approval_gate.py --parent <親エピックGID> --handoff <path> -y`
2. **チャット**で依頼者へ Handoff 要約と【承認】サブ URL を提示
3. 依頼者: Asana UI で **`Approval Result=OK/NG`** → 【承認】complete
4. 和久桶さんへチャットで再開依頼 → `handoff_to_asana.py --require-review-result`

**禁止（opt-in 時）:** チャット「承認待ち」のみで止め、依頼者の Asana complete を待たない。

CLI: [`create_planning_approval_gate.py`](../../tools/create_planning_approval_gate.py) · [`check_planning_approval_gate.py`](../../tools/check_planning_approval_gate.py)

## org-os と PM review gate — RETIRED

> **廃止（2026-06-09）** — org-os suspend/resume · `--record-wait` は使わない。PM review gate opt-in 時も **チャット確認 + Asana UI complete**。

## 参照

- [`chat-driven-ops.md`](chat-driven-ops.md) — 本番運用 SSOT
- [`approval-flow.md`](approval-flow.md) — 承認サブ ↔ 親 epic CF 写像
- [`workflow-io-contract.md`](workflow-io-contract.md) — パイプライン全体
- [`pm-assign-review-gate.md`](pm-assign-review-gate.md) — PM review gate 詳細
- [`dispatch-auto-proceed-ssot.md`](dispatch-auto-proceed-ssot.md) — L2 execution dispatch 自動進行
- [`asana-driven-ops.md`](asana-driven-ops.md) — **RETIRED**（Asana 自動化の履歴）
