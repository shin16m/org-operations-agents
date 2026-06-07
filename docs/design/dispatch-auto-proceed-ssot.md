# L2 execution dispatch 自動進行 SSOT

| 版 | 1.0 |
| 日付 | 2026-06-07 |
| エピック | `1215473463319556` |
| 関連 | [`planning-gate-vs-pm-review-gate.md`](planning-gate-vs-pm-review-gate.md) · [`workflow-io-contract.md`](workflow-io-contract.md) · SSOT id: `dispatch-auto-proceed-ssot` |

## 問題

`asana_execute`（または planning 子 `DeptWorkComplete`）のあと、workflow-orchestrator / エージェントが **「続けて UX dispatch まで進めますか？」** 等の **チャット確認** を挟むことがある。planning gate は **デフォルト opt-out** だが、**L2 task-dispatcher → PM 委譲** に同等の SSOT がなかった。

## 3 層のゲート（整理）

| ゲート | 段階 | デフォルト | opt-in トリガー |
|--------|------|------------|-----------------|
| **planning gate** | L3 企画 | 要約提示後 **同一セッションで `handoff_to_asana`** | `human_planning_approval` / `ORG_OPS_PLANNING_APPROVAL_GATE=1` |
| **L2 execution dispatch** | L1/L2 · `asana_execute` 後 | **未完了 execution 系子を 1 件 task-dispatcher → PM prompt_snippet まで自動進行**（チャット確認しない） | `human_execution_dispatch` / `ORG_OPS_EXECUTION_DISPATCH_CONFIRM=1` |
| **PM review gate** | L3 各 PM intake 後 | **gate 省略**（`check_pm_review_gate` exit 0） | `human_review_gate` / `ORG_OPS_PM_REVIEW_GATE=1` |

## L2 デフォルト（opt-out）

1. 企画子 `DeptWorkComplete` または `asana_execute` 完了を検知
2. `fetch_task.py --list-subtasks` で未完了 execution 系子を列挙（配賦順: ux → development / analysis → governance → audit）
3. 同一 department 内は **Execution Order CF 昇順**（未設定時は GID 昇順）で並べ、**先頭 1 件**を [`task-dispatcher`](../../skills/platform/task-dispatcher/SKILL.md) へ委譲し **entry PM 用 prompt_snippet を返す**（[`org-os-product-io.md`](org-os-product-io.md) §5）
4. **利用者への「進めますか？」確認はしない**（チャット「すすめて」は planning gate デフォルトと同様に有効）

**禁止（デフォルト）:**

- 「続けて dispatch しますか？」のみで停止
- L2 dispatch を省略して PM intake / ワーカー成果物に直接着手

**許容:**

- `asana_execute` セッションと **PM intake セッションの分離**（成果物・doc 更新は別セッション）

## L2 opt-in（評価・監査）

トリガー（いずれか）:

- Handoff `meta.human_execution_dispatch: true`
- env `ORG_OPS_EXECUTION_DISPATCH_CONFIRM=1`
- epic notes `human_execution_dispatch: yes`
- CLI `--require-human-dispatch-confirm`（将来 · `task_dispatcher.py`）

挙動:

1. 未完了 execution 系子の一覧と次の department を提示
2. 利用者の明示合図（チャット「すすめて」等）後に task-dispatcher 実行
3. Asana ドリブン RESUME 後も同様（[`approval-flow.md`](approval-flow.md) 更新済み）

CLI ヘルパー: [`execution_dispatch_util.py`](../../tools/execution_dispatch_util.py) の `human_execution_dispatch_requested()`

## 担当

| 役割 | 責務 |
|------|------|
| **workflow-orchestrator** | 企画完了後 · RESUME 後の L2 自動 dispatch（デフォルト） |
| **task-dispatcher** | prompt_snippet 生成のみ（チーム内作業しない） |
| **各 PM** | intake（`pm_assign_subtasks`）→ L3b worker dispatch |

## 参照

- [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md)
- [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md)
- 先行: PM review gate opt-in epic `1215465361526049`
