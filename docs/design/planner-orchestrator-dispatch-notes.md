# issue-story-planner / workflow-orchestrator 追記

## issue-story-planner — department 付与チェックリスト

企画 Handoff の各 `subtasks[]` について:

1. **実行系**（実装・検証・整備でリポジトリ変更する子）には `department` を付与する。
2. 推奨値: `development`（開発チーム）| `analysis`（分析・調査）| `planning`（追加の企画・設計子）。
3. bootstrap 企画子（intake 時の最初の 1 件）は orchestrator が `department: planning` で作成済み。
4. 同一エピック内で planning / development / analysis が混在してよい。

## workflow-orchestrator — フロー

```
1. intake: 生課題 → bootstrap Handoff 生成
2. bootstrap: 親 + 企画子 1 件を Asana 作成
3. dispatch: 企画子 → planning-delivery（planning-pm）
4. 企画完了（DeptWorkComplete）後:
   fetch_task.py --gid <parent> --list-subtasks
5. completed=false の execution 系子を 1 件ずつ dispatch
6. 子完了のたびに 5 に戻る
7. 全子 completed → エピック完了報告
```

## gate との関係

- **gate**（`handoff_approved`）は **planning-pm（pm_gate）** が担当。
- execution 系子の dispatch は gate **後**（企画 Asana 投入後）。
