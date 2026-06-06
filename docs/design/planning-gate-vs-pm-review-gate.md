# planning gate と PM review gate — 整理 SSOT

| 版 | 1.3 |
| 日付 | 2026-06-05 |
| エピック | `1215086341081688` · F4 · **`1215465361526049`**（PM review gate opt-in） |

## 2 種類の人間ゲート

| ゲート | 段階 | 担当 PM | 承認対象 | トリガー CLI | チェック CLI |
|--------|------|---------|----------|--------------|--------------|
| **planning gate** (`handoff_approved`) | L3 企画 | planning-pm | Handoff 要約 · execution 系子の Asana 投入 | `create_approval_subtask.py`（【承認】· **親 epic**）→ `--record-wait` → RESUME 後 `handoff_to_asana.py --require-review-result` | 【承認】サブ complete + `PlanReviewResult` · **チャット承認はレガシーのみ** |
| **PM review gate** (`pm_review_gate`) | L3 execution 各 PM | product-manager / ux-pm / analytics-pm / governance-pm / audit-pm | **作成済み worker サブ**の構成・担当 slug | **opt-in のみ** `create_pm_review_gate.py` | `check_pm_review_gate.py` exit 0（gate 無しも 0） |

## 混同しやすい点

- **planning gate の「承認」** = execution 系子タスクを Asana に**作ってよい**（実装開始の合図**ではない**）。
- **PM review gate の「完了」** = 当該 PM 子の **L3b worker dispatch 可**（`pm_emit_worker_prompt` 前）。**デフォルトでは gate 自体を作らない**（評価・監査時のみ opt-in）。
- チャットの「すすめて」「承認」は **planning gate のみ**有効。PM review gate は **opt-in 時のみ** Asana UI で【レビュー】サブを complete する。

## F1: Asana dependencies

`create_pm_review_gate.py` 実行後、各 worker サブは【レビュー】サブに **Asana dependency** を付与する（`addDependencies`）。  
人間が review サブを complete するまで worker サブは Asana 上もブロックされる。

## planning gate Asana 化（Phase 1 · intake-asana 必須）

Asana ドリブン運用（intake-asana · auto-intake · 本番プロジェクト）では planning gate を **【承認】サブ + `--record-wait` + A/B/C** のみとする（詳細: [`asana-driven-ops.md`](asana-driven-ops.md)）。

1. planning-pm: `PlanReviewResult` 通過後、`create_approval_subtask.py --parent <親エピックGID>` で要約 notes を付与
   - サブ作成と同時に **親 `OS State=Waiting`** + **`Approval Required=Yes`** + **`OS Suspend Reason=Approval`**
   - サブ assignee = **`ASANA_DEFAULT_HUMAN_APPROVER_GID`**
2. orchestrator / planning-pm: `asana_ops_poller.py --record-wait <親エピックGID> <承認サブGID> <URL>` → SuspendedSession → **セッション終了**
3. 依頼者: Asana UI で **`Approval Result=OK/NG`** → 【承認】complete
4. `approval_helper` → `wakuoke_resume_scan` → `handoff_to_asana.py --require-review-result`

**禁止:** チャット「承認待ち」のみ（【承認】+ record-wait 省略）。

チャット「承認」は **workflow 短絡を明示したレガシー手動 intake** のみ。Asana ドリブン時は【承認】complete を正とする。

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
