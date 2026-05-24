# Asana 担当種別カスタムフィールド — 運用 SSOT

| 版 | 1.2 |
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
| `handoff_to_asana.py` 親タスク create / sync 更新 | `AI` |
| `handoff_to_asana.py` が新規作成する **execution 系 department 子**（エピック直下） | `AI`（addProject なし · PUT のみ） |
| `pm_assign_subtasks.py` の **PM 進行親**（`--update-parent-assignee` 対象） | `AI` |
| `create_approval_subtask.py` / `create_pm_review_gate.py`（【レビュー】/【承認】） | **human** |
| `create_subtask`（PM 配下の worker サブ） | **設定しない** |

### worker サブに CF を付けない理由

プロジェクトスコープ CF を worker サブに付ける従来手段は `addProject` だが、**addProject したサブタスクはプロジェクト一覧・セクション直下に独立表示される**（[`asana-subtask-layout-fix-dryrun`](../verification/asana-subtask-layout-fix-dryrun.md)）。  
worker サブは notes の `担当:` で判別する。**execution PM 子**（エピック直下の department 子）のみ PUT で `AI` を試行する。

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
- layout-fix: [`docs/verification/asana-subtask-layout-fix-dryrun.md`](../verification/asana-subtask-layout-fix-dryrun.md)
- dryrun: [`docs/verification/asana-assignee-type-field-dryrun.md`](../verification/asana-assignee-type-field-dryrun.md)
