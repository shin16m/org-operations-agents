# 組織モデル・子タスク単位ディスパッチ・完了集約

エピック: 組織配賦・子タスク単位 PM ワークフロー（タスク 1）。

## 三層レイヤー

```
┌─────────────────────────────────────────────────────────────┐
│ L1 企画レイヤー（1 回 / 親エピック）                          │
│   workflow-orchestrator → issue-story-planner → plan-reviewer │
│   → gate → asana-buddy（親 + 子タスク作成）                  │
│   成果物: Asana 親エピック + 子タスク群 ＝ 企画書             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ L2 配賦レイヤー（子タスク 1 件ごと）                          │
│   workflow-orchestrator → task-dispatcher                   │
│   入力: 子 task_gid + department                            │
│   出力: 課 workflow の entry へ委譲（prompt_snippet）         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ L3 課内レイヤー（子タスク 1 件 = workflow インスタンス 1 本）  │
│   開発課: product-manager ハブ → doc-writer / developer / …   │
│   分析課: analysis-delivery（プレースホルダ）                 │
│   完了: DeptWorkComplete → オーケストレーター                │
└─────────────────────────────────────────────────────────────┘
```

## 配賦単位

| 項目 | ルール |
|------|--------|
| ディスパッチ単位 | Asana **子タスク 1 件** |
| 課内 workflow | 子ごとに**独立インスタンス**（別 PM セッション） |
| 親エピック | 企画書。全子が完了するまでエピック完了としない |
| 混在 | 同一親下に `development` / `analysis` の子が共存しうる |

## 責務表

| 役割 | レイヤー | やること | やらないこと |
|------|----------|----------|--------------|
| **workflow-orchestrator** | L1, L2 入口 | intake / gate；execute 後の子一覧と dispatch 委譲；全子完了の集約報告 | 要件定義・コーディング |
| **issue-story-planner** | L1 | Handoff・各子に `department` 推奨 | Asana API |
| **plan-reviewer** | L1 | エピック単位の企画レビュー | 課内コードレビュー |
| **asana-buddy** | 横断 | 親+子**作成**、**読取**、**完了マーク** | 作業本体 |
| **task-dispatcher** | L2 | `department` → 課 workflow へルーティング | 課内作業 |
| **product-manager** | L3（開発課） | 子 1 件の状態機械・依頼・分岐・完了報告 | Handoff 新規作成 |
| **doc-writer / developer / reviewer** | L3 | PM からの委譲作業 | ディスパッチ |

## 子完了 → 親エピック完了

1. オーケストレーターは `fetch_task.py --gid <parent> --list-subtasks` で未完了子を列挙する。
2. 未完了子ごとに L2→L3 を起動（順次または並行は運用判断）。
3. 各子完了時に `DeptWorkComplete`（または課内で `complete_task.py -y`）を受け取る。
4. **すべての子**が `completed` になったら、利用者へ「プロダクト開発完了」（親エピック完了）を報告する。

## asana-buddy の位置づけ

変更なし: **作成・読取・完了**の横断サービス。課内エージェントは API を直叩かずスクリプトを呼ぶ。

## 関連

- ルーティング: [`workflows/organizations.yaml`](../../workflows/organizations.yaml)
- 開発課 workflow: [`workflows/development-delivery.yaml`](../../workflows/development-delivery.yaml)
- I/O: [`dept-work-io.md`](dept-work-io.md)
- 旧単一ワーカー: [`task-execution-boundary.md`](task-execution-boundary.md)
