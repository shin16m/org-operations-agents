# workflow-orchestrator

**課題の入口。** 生課題を受け取り（intake）、plan → review の後に execute 可否を判定（gate）する。

詳細: [`SKILL.md`](SKILL.md)

## 使い方（2 系統）

### 1. intake — 課題を渡す（ここから開始）

```
あなたは workflow-orchestrator スキルです（intake モード）。
課題: 〈依頼内容を自然言語で〉
issue-story-planner への prompt_snippet を返してください。
```

返却されたプロンプトで **issue-story-planner** を起動 → Handoff JSON を保存。

### 2. gate — review 後

Handoff と `PlanReviewResult`（`passed` 必須）を渡す:

```
あなたは workflow-orchestrator スキルです（gate モード）。
execute に進めるか、差し戻し先を示してください。
```

通過後 **asana-buddy** で Asana 投入。

## 移行

以前 planner 先頭で運用していた場合も、**新規依頼は orchestrator（intake）から**始めてください（[`README.md`](../../README.md)）。

## 参照

- workflow: [`workflows/default.yaml`](../../workflows/default.yaml) v2
- I/O: [`docs/design/workflow-session-io.md`](../../docs/design/workflow-session-io.md)
