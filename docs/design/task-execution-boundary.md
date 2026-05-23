# 計画フェーズと実行フェーズの責務境界

## ギャップ（解消済み）

| フェーズ | 現状 |
|----------|------|
| 受付 | intake → bootstrap → dispatch（企画） |
| 企画 | planning-delivery（Handoff → review → gate → Asana） |
| 実行 | task-dispatcher → チーム PM → ワーカー（L3b） |

## 分担表

| 責務 | `asana-buddy` | チーム PM + ワーカー |
|------|---------------|----------------------|
| Handoff から親＋子タスク**作成** | はい | いいえ |
| Handoff **新規作成** | いいえ | いいえ（→ issue-story-planner） |
| 既存タスクの **読取**（name / notes / completed） | はい（`fetch_task.py`） | ワーカーが利用 |
| サブタスクの **完了マーク** | はい（`complete_task.py`） | PM / ワーカー完了後 |
| notes の `done_when` に沿った**作業本体** | いいえ | はい（各 worker SKILL） |
| 専用ツール・新規スキルが要る場合 | いいえ | **agent-creater へ委譲** |

## 原則

- **default v3** の L1 終端は dispatch（企画チームへ初回配賦）。実行は dispatch 後の各 `*-delivery.yaml`。
- チーム間 I/O: [`dept-work-io.md`](dept-work-io.md)（`DispatchRequest` / `DeptWorkComplete`）
