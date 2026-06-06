# planning gate と PM review gate — 整理 SSOT

| 版 | 1.5 |
| 日付 | 2026-06-06 |
| エピック | `1215086341081688` · F4 · **`1215465361526049`**（PM review gate opt-in）· planning / retro gate opt-in |

## 2 種類の人間ゲート

| ゲート | 段階 | 担当 PM | 承認対象 | トリガー CLI | チェック CLI |
|--------|------|---------|----------|--------------|--------------|
| **planning gate** (`handoff_approved`) | L3 企画 | planning-pm | Handoff 要約 · execution 系子の Asana 投入 | **デフォルト:** 要約提示後 **同一セッションで** `handoff_to_asana.py --require-review-result`（【承認】・`--record-wait` 不要）。**opt-in:** `create_planning_approval_gate.py` → `--record-wait` → RESUME 後 `handoff_to_asana.py` | **デフォルト:** `PlanReviewResult` 通過で可。**opt-in:** 【承認】サブ complete + `PlanReviewResult` |
| **PM review gate** (`pm_review_gate`) | L3 execution 各 PM | product-manager / ux-pm / analytics-pm / governance-pm / audit-pm | **作成済み worker サブ**の構成・担当 slug | **opt-in のみ** `create_pm_review_gate.py` | `check_pm_review_gate.py` exit 0（gate 無しも 0） |

## 混同しやすい点

- **planning gate の「承認」** = execution 系子タスクを Asana に**作ってよい**（実装開始の合図**ではない**）。
- **PM review gate の「完了」** = 当該 PM 子の **L3b worker dispatch 可**（`pm_emit_worker_prompt` 前）。**デフォルトでは gate 自体を作らない**（評価・監査時のみ opt-in）。
- チャットの「すすめて」「承認」は **planning gate デフォルト（opt-out）** で有効。planning gate **opt-in 時のみ**【承認】サブ complete が必須。PM review gate も **opt-in 時のみ** Asana UI で【レビュー】サブを complete する。

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
- [`complete_task.py`](../../skills/platform/asana-buddy/optional/complete_task.py) — 【レビュー】/【承認】はエージェント complete 禁止（exit 3）
