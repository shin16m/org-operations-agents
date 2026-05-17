# issue-story-planner / workflow-orchestrator 追記案（最小）

エピック: 組織配賦（タスク 5）。**本格 SKILL 更新はタスク 11**（Handoff v1.2）。

## issue-story-planner — department 付与チェックリスト

企画 Handoff の各 `subtasks[]` について:

1. **実行系**（実装・検証・整備でリポジトリ変更する子）には `department` を付与する。
2. 推奨値: `development`（開発課）| `analysis`（分析・調査のみ）| `planning`（企画・設計のみで L3 不要）。
3. v1.1 のみのときは `pillar` に「開発課」等を含め、dispatcher が [`organizations.yaml`](../../workflows/organizations.yaml) の `pillar_defaults` で推定する。
4. 同一エピック内で development / analysis が混在してよい。

## workflow-orchestrator — execute 後フロー（擬似）

**実装:** タスク 10（SKILL 本追記）。ここでは挙動のみ固定。

```
1. execute 完了（親 GID 確定）
2. fetch_task.py --gid <parent> --list-subtasks
3. completed=false の子を列び、先頭 1 件（または利用者指定 GID）を選ぶ
4. 子の notes / Handoff から department を解決
5. task-dispatcher 用 prompt_snippet を返す:
   「DispatchRequest で task_gid=… department=… を渡し、課 workflow を起動」
6. 子完了（DeptWorkComplete）のたびに 3 に戻る
7. 全子 completed → 利用者へエピック完了報告
```

## gate モードとの関係

- **gate** は従来どおり L1 の execute 可否のみ。
- L2 dispatch は gate **後**の別セッションでよい（`with-dispatch.yaml` の `dispatch` 段階）。
