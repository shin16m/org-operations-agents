# planning gate と PM review gate — 整理 SSOT

| 版 | 1.6 |
| 日付 | 2026-06-07 |
| エピック | `1215086341081688` · F4 · **`1215465361526049`**（PM review gate opt-in）· **`1215473463319556`**（L2 dispatch 自動進行） |

## 3 種類のゲート（人間 / 自動）

| ゲート | 段階 | 担当 | 対象 | デフォルト | opt-in |
|--------|------|------|------|------------|--------|
| **planning gate** (`handoff_approved`) | L3 企画 | planning-pm | Handoff 要約 · execution 系子 Asana 投入 | 要約提示後 **同一セッションで** `handoff_to_asana.py` | `create_planning_approval_gate.py` · `human_planning_approval` |
| **L2 execution dispatch** | L1/L2 · `asana_execute` 後 | workflow-orchestrator | 未完了 execution 系子 → task-dispatcher → PM | **自動進行**（チャット確認しない） | `human_execution_dispatch` · `ORG_OPS_EXECUTION_DISPATCH_CONFIRM=1`（[`dispatch-auto-proceed-ssot.md`](dispatch-auto-proceed-ssot.md)） |
| **PM review gate** (`pm_review_gate`) | L3 各 PM | product-manager / ux-pm / … | worker サブ構成・担当 slug | **gate 省略** | `create_pm_review_gate.py` · `human_review_gate` |

## 混同しやすい点

- **planning gate の「承認」** = execution 系子タスクを Asana に**作ってよい**（実装開始の合図**ではない**）。
- **L2 execution dispatch** = 投入済み execution 系子を **task-dispatcher → PM** へ配賦。**デフォルトはチャット確認なし**（「続けて dispatch しますか？」禁止）。
- **PM review gate の「完了」** = 当該 PM 子の **L3b worker dispatch 可**（`pm_emit_worker_prompt` 前）。**デフォルトでは gate 自体を作らない**（評価・監査時のみ opt-in）。
- チャットの「すすめて」「承認」は **planning gate · L2 dispatch デフォルト（opt-out）** で有効。planning gate **opt-in 時のみ**【承認】サブ complete が必須。PM review gate も **opt-in 時のみ** Asana UI で【レビュー】サブを complete する。

## F1: Asana dependencies

`create_pm_review_gate.py` 実行後、各 worker サブは【レビュー】サブに **Asana dependency** を付与する（`addDependencies`）。  
人間が review サブを complete するまで worker サブは Asana 上もブロックされる。

## planning gate デフォルト（opt-out · 全 intake 経路）

`PlanReviewResult` 通過後:

1. planning-pm: Handoff 要約を提示
2. **同一セッションで** `handoff_to_asana.py --require-review-result` を実行
3. 【承認】サブ・`--record-wait` は **作らない**

## planning gate opt-in（評価・監査 · Asana ドリブン運用）

トリガー（いずれか）:

- `create_planning_approval_gate.py --require-human-approval`
- Handoff `meta.human_planning_approval: true`
- env `ORG_OPS_PLANNING_APPROVAL_GATE=1`
- epic notes `human_planning_approval: yes`

1. planning-pm: `create_planning_approval_gate.py --parent <親エピックGID> --handoff <path> -y`
2. orchestrator: `asana_ops_poller.py --record-wait <親> <承認サブ> <URL>` → **セッション終了**
3. 依頼者: Asana UI で **`Approval Result=OK/NG`** → 【承認】complete
4. `approval_helper` → `wakuoke_resume_scan` → `handoff_to_asana.py --require-review-result`

**禁止（opt-in 時のみ）:** チャット「承認待ち」のみ（【承認】+ record-wait 省略）。

CLI: [`create_planning_approval_gate.py`](../../tools/create_planning_approval_gate.py) · [`check_planning_approval_gate.py`](../../tools/check_planning_approval_gate.py)

## org-os と PM review gate

| ゲート | org-os suspend 対象 | reason |
|--------|---------------------|--------|
| planning 【承認】 | **親 epic** | `Approval`（`create_approval_subtask`） |
| PM 【レビュー】 | **親 epic**（PM 子 GID から解決） | `Human Review`（`create_approval_subtask` / `--record-wait`） |

`--record-wait` の第 1 引数は planning では親 epic · PM review では **PM 子 GID** 可。session JSON に `epic_gid` を保存。`approval_helper` は `resolve_epic_gid` で親 epic を resume。

## 参照

- [`asana-driven-ops.md`](asana-driven-ops.md) — スキャン · 保留再開 SSOT
- [`approval-flow.md`](approval-flow.md) — 承認サブ ↔ 親 epic CF 写像 SSOT
- [`workflow-io-contract.md`](workflow-io-contract.md) — パイプライン全体
- [`pm-assign-review-gate.md`](pm-assign-review-gate.md) — PM review gate 詳細
- [`dispatch-auto-proceed-ssot.md`](dispatch-auto-proceed-ssot.md) — L2 execution dispatch 自動進行
- [`complete_task.py`](../../skills/platform/asana-buddy/optional/complete_task.py) — 【レビュー】/【承認】はエージェント complete 禁止（exit 3）
