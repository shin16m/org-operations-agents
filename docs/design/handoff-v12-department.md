# Handoff v1.2 — department フィールド

エピック: 組織配賦（タスク 2）。

## 変更点（v1.1 → v1.2）

| 項目 | v1.1 | v1.2 |
|------|------|------|
| `schema_version` | `"1.1"` | `"1.2"` |
| `subtasks[].department` | なし | 任意 enum |

## department 値

| 値 | 課 | L2 先 workflow |
|----|-----|----------------|
| `development` | 開発課 | `development-delivery` |
| `analysis` | 分析課 | `analysis-delivery` |
| `planning` | 企画課 | L1 のみ（通常は dispatch しない） |

## pillar → department（v1.2 未設定時）

[`workflows/organizations.yaml`](../../workflows/organizations.yaml) の `pillar_defaults` を参照。

## Asana notes への反映

`handoff_to_asana` は `department` があるとき notes 先頭に `課: {department}\n` を付与（v1.1 互換: `load_handoff` は 1.1 / 1.2 両方受理）。

## planner 追記

本格追記は [`issue-story-planner/SKILL.md`](../../skills/issue-story-planner/SKILL.md) タスク 11。チェックリストは [`planner-orchestrator-dispatch-notes.md`](planner-orchestrator-dispatch-notes.md)。
