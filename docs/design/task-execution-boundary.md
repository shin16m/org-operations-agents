# 計画フェーズと実行フェーズの責務境界

タスク 1 成果物（エピック: タスク実行フェーズ）。

## ギャップ

| フェーズ | 現状 | 不足 |
|----------|------|------|
| 受付 | intake → bootstrap → dispatch（企画） | — |
| 企画 | planning-delivery（Handoff → review → gate → Asana） | — |
| 実行 | task-dispatcher → チーム workflow | 過渡期 task-executor |

## 分担表

| 責務 | `asana-buddy` | `task-executor` |
|------|---------------|-----------------|
| Handoff から親＋子タスク**作成** | はい | いいえ |
| Handoff **新規作成** | いいえ | いいえ |
| 既存タスクの **読取**（name / notes / completed） | はい（API スクリプト） | 依頼（スクリプト呼び出し） |
| サブタスクの **完了マーク** | はい（API スクリプト） | 依頼（完了判定後） |
| notes の `done_when` に沿った**作業本体** | いいえ | はい |
| 専用ツール・新規スキルが要る場合 | いいえ | **agent-creater へ委譲** |

## 原則

- **task-executor** は `AsanaBuddyHandoff` を再生成しない。Asana 上のタスク GID と notes を読み、リポジトリ内変更または実行手順を行う。
- **default v3** の L1 終端は dispatch（企画チームへ初回配賦）。実行フェーズは dispatch 後のチーム workflow または [`workflows/with-execution.yaml`](../../workflows/with-execution.yaml)（deprecated task-executor）。
