# オーケストレーター入口 workflow ドライラン

タスク 5 成果物（intake epic 完了後）。workflow v2: **intake → plan → review → gate → execute**

## 前提

- [`workflows/default.yaml`](../../workflows/default.yaml) `version: "2"`
- [`docs/design/workflow-session-io.md`](../design/workflow-session-io.md)
- タスク 3・4（orchestrator SKILL、README/E2E）反映済み

## 手順（架空課題）

| # | step | スキル | 確認内容 |
|---|------|--------|----------|
| 1 | intake | workflow-orchestrator | 課題「README に移行一行を足す」→ plan 用 `prompt_snippet` が返る |
| 2 | plan | issue-story-planner | Handoff v1.1 JSON を保存 |
| 3 | review | plan-reviewer | `PlanReviewResult.status` = `passed` または `passed_with_notes` |
| 4 | gate | workflow-orchestrator | `review_passed` 確認後、asana-buddy 用 `prompt_snippet` |
| 5 | execute | asana-buddy | `handoff_to_asana.py`（本記録では Asana 未投入でも可） |

## 二回の orchestrator 起動

1. **intake** — セッション開始・生課題のみ
2. **gate** — Handoff + PlanReviewResult 添付

「単一窓口」≠ 1 回の呼び出しであることを手順で確認した。

## 再現用プロンプト（要約）

**intake:**

```
あなたは workflow-orchestrator スキルです（intake モード）。
課題: 〈テスト用の短い依頼〉
issue-story-planner への prompt_snippet を返してください。
```

**gate:**

```
あなたは workflow-orchestrator スキルです（gate モード）。
添付の PlanReviewResult と Handoff を確認し、execute に進める prompt_snippet を返してください。
```

## 結果

- 2026-05-17: リポジトリ上の SKILL / workflow / E2E を intake 起点に更新済み。上記 5 段階が文書間で一致。
- Asana エピック `1214873888809993`（オーケストレーター入口化）を本変更と同期しサブタスク 1–5 を完了マーク。

参照 Handoff: [`skills/planning/issue-story-planner/examples/handoff.orchestrator-intake-entry.json`](../../skills/planning/issue-story-planner/examples/handoff.orchestrator-intake-entry.json)
