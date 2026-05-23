# issue-story-planner

課題の整理・解決ストーリー・Asana 向けタスク案をまとめ、**AsanaBuddyHandoff v1.1** JSON を出力するスキルです。

詳細・I/O 契約: [`SKILL.md`](SKILL.md)

## 標準パイプライン

通常は [`workflow-orchestrator`](../workflow-orchestrator/README.md)（**intake**）から委譲されて起動します。

```
orchestrator（intake）→ 本スキル（plan）→ plan-reviewer → orchestrator（gate）→ asana-buddy
```

## 使い方（Copilot / Cursor）

```
あなたは issue-story-planner スキルです。テーマ「〈課題〉」について課題整理・解決ストーリー・タスク案を出し、
AsanaBuddyHandoff v1.1（各 subtask に background・summary・done_when 必須）の JSON を1つだけ出力してください。
```

## Handoff 例

| ファイル | 用途 |
|----------|------|
| [`examples/handoff.example.json`](examples/handoff.example.json) | 汎用 |
| [`examples/handoff.agent-workflow-orchestration.json`](examples/handoff.agent-workflow-orchestration.json) | 基盤エピック |
| [`examples/handoff.orchestrator-intake-entry.json`](examples/handoff.orchestrator-intake-entry.json) | 入口化エピック |
| [`examples/handoff.skill-review-remediation.json`](examples/handoff.skill-review-remediation.json) | レビュー指摘是正 |
| [`examples/handoff.analysis-delivery.json`](examples/handoff.analysis-delivery.json) | 分析課 delivery |

スキーマ: [`schemas/asana-buddy-handoff.v1.schema.json`](schemas/asana-buddy-handoff.v1.schema.json)

## 注意

- 新規 `skills/<slug>/` は作らない → [`agent-creater`](../agent-creater/SKILL.md)
- Handoff 出力後は **plan-reviewer 必須**（[`workflows/default.yaml`](../../workflows/default.yaml)）
