# workflow-orchestrator

**課題の入口。** 生課題を受け取り（intake）、bootstrap で最小 Asana を作成し、企画チームへ dispatch する。

詳細: [`SKILL.md`](SKILL.md)

## 使い方

### 1. intake — 課題を渡す（ここから開始）

```
あなたは workflow-orchestrator スキルです（intake モード）。
課題: 〈依頼内容を自然言語で〉
bootstrap 用最小 Handoff を生成し、bootstrap → dispatch（企画チーム）まで進めてください。
```

### 2. 企画完了後 — execution 系 dispatch

企画チームから `DeptWorkComplete` を受け取ったら、未完了の development / analysis 子を task-dispatcher で順次配賦する。

### 3. 作業完了後 — Asana 同期

各チーム PM が `comment_task.py` → `complete_task.py -y` を実行。全子完了後に親エピックも完了にしてから利用者へ報告する。

## 企画 gate について

Asana 本番投入前の人間承認（`handoff_approved`）は **planning-pm** が担当。orchestrator の gate モード（v2）は v3 では使用しない。

## workflow の選び方

| 目的 | ファイル |
|------|----------|
| 標準（企画 dispatch まで） | [`workflows/default.yaml`](../../../workflows/default.yaml) v3 |
| + execution 系 dispatch ループ | [`workflows/with-dispatch.yaml`](../../../workflows/with-dispatch.yaml) |
| 企画チーム L3 | [`workflows/planning-delivery.yaml`](../../../workflows/planning-delivery.yaml) |

## 参照

- E2E: [`docs/e2e/default-workflow.md`](../../../docs/e2e/default-workflow.md)
- I/O: [`docs/design/workflow-session-io.md`](../../../docs/design/workflow-session-io.md)
