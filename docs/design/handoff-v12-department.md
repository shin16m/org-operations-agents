# Handoff v1.2 — department フィールド

エピック: 組織配賦（タスク 2）。

## 変更点（v1.1 → v1.2）

| 項目 | v1.1 | v1.2 |
|------|------|------|
| `schema_version` | `"1.1"` | `"1.2"` |
| `subtasks[].department` | なし | 任意 enum |

## department 値

| 値 | チーム | L3 先 workflow |
|----|-----|----------------|
| `planning` | 企画チーム | `planning-delivery`（bootstrap 企画子・企画専用子） |
| `development` | 開発チーム | `development-delivery` |
| `analysis` | 分析チーム | `analysis-delivery` |
| `ux` | UX チーム | `ux-delivery` |
| `governance` | 組織改善チーム | `governance-delivery` |
| `audit` | 監査チーム | `audit-delivery` |

## pillar → department（v1.2 未設定時）

[`workflows/organizations.yaml`](../../workflows/organizations.yaml) の `pillar_defaults` を参照。

## Asana notes への反映

`handoff_to_asana` は `department` があるとき notes 先頭に `チーム: {department}\n` を付与（**読取は legacy `課:` も受理**）。v1.1 互換: `load_handoff` は 1.1 / 1.2 両方受理。

## Handoff とチーム間 I/O

`AsanaBuddyHandoff` は**企画チームのチーム内成果物**。他チームの公式入力は Asana 子タスク + notes（[`department-model.md`](department-model.md)）。`subtasks[].department` は `handoff_to_asana` 投入時に notes の `チーム:` 行へ反映され、**task-dispatcher は Handoff ファイルを読まない**。

## planner 追記

企画 Handoff の execution 系子には `department` を付与する。bootstrap 企画子は `planning` 固定。

- チェックリスト: [`issue-story-planner/SKILL.md`](../../skills/planning/issue-story-planner/SKILL.md) · [`handoff-v12-department.md`](handoff-v12-department.md)
