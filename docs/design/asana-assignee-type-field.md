# Asana 担当種別カスタムフィールド — 運用 SSOT

| 版 | 1.0 |
| 日付 | 2026-05-24 |

## 目的

Asana プロジェクトの **担当種別** enum CF で、タスクが **AI エージェント運用** か **人間担当** かを一覧で判別する。

| 値 | 意味 |
|----|------|
| **AI** | org-ops CLI / エージェント workflow が作成・管理するタスク |
| **human** | 利用者が Asana 上で人間を assignee にしたタスク（手動設定） |

## GID（プロジェクト `1214771428861230`）

| 種別 | GID |
|------|-----|
| フィールド「担当種別」 | `1215082835199209` |
| enum `AI` | `1215082835199211` |
| enum `human` | `1215082835199210` |

`.env` で上書き可能: [`skills/platform/asana-buddy/optional/.env.example`](../../skills/platform/asana-buddy/optional/.env.example)

## org-ops が自動設定するタイミング

| CLI / 関数 | 担当種別 |
|------------|----------|
| `handoff_to_asana.py` 親タスク create | `AI` |
| `create_subtask`（handoff / pm_assign_subtasks / fix subtask 等） | `AI` |

サブタスクは **親と同じプロジェクトへ `addProject` した後** に CF を設定する（プロジェクトスコープ CF のため）。

## human の設定

org-ops は **Asana ユーザー assignee API を使わない** ため、`human` は次のいずれか:

1. Asana UI でタスクに人間を assign したあと、**手動で CF を human に変更**
2. 将来: 専用 CLI `set_assignee_type(task, human)`（本エピックスコープ外でも可）

## 無効化

テスト・他プロジェクト向け:

```env
ASANA_ASSIGNEE_TYPE_DISABLED=true
```

## 参照

- ソース intake-asana: `1215082835252581`
- dryrun: [`docs/verification/asana-assignee-type-field-dryrun.md`](../verification/asana-assignee-type-field-dryrun.md)
