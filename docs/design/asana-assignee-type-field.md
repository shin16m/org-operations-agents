# Asana 担当種別カスタムフィールド — 運用 SSOT

| 版 | 1.5 |
| 日付 | 2026-05-24 |

## 目的

Asana プロジェクトの **担当種別** enum CF で、タスクの **担当メンバー（assignee）が AI エージェントか人間か** を一覧で判別する。

| 値 | 意味 |
|----|------|
| **AI** | 担当メンバーが **AI エージェント**（org-ops CLI / workflow が作成・管理する実行タスク） |
| **human** | 担当メンバーが **人間**（依頼者・承認者など Asana 上で人が完了するタスク） |

**`human` は「手動で CF を触ったタスク」に限らない。** 人間が作成した AI 実行タスクは **AI**、エージェントが作成した【承認】/【レビュー】は **human**（担当=人間）を org-ops が自動設定する。

### 想定運用（設定者 × 担当種別）

| 作成者 | タスク内容 | 担当種別 | 設定者 |
|--------|------------|----------|--------|
| 人間 | AI に実施させるタスク | **AI** | 人間 |
| 人間 | 人間が実施するタスク | **human** | 人間 |
| エージェント | 人の承認タスク（【レビュー】/【承認】等） | **human** | エージェント |
| エージェント | AI で実施可能なタスク | **AI** | エージェント |

`.env` で上書き可能: [`skills/platform/asana-buddy/optional/.env.example`](../../skills/platform/asana-buddy/optional/.env.example)

**プロジェクトごとに CF GID が異なる。** 切替時は [`tools/sync_assignee_type_env.py`](../../tools/sync_assignee_type_env.py) で `.env` を同期する。

```powershell
python tools/sync_assignee_type_env.py --project <PROJECT_GID> --dry-run
python tools/sync_assignee_type_env.py --project <PROJECT_GID> --write -y
```

## API 400 — パターンと workaround

| # | パターン | API メッセージ例 | 対処 |
|---|----------|------------------|------|
| 1 | **GID 不一致** | `Custom field with ID … is not on given object` | `sync_assignee_type_env.py --write` で正しいプロジェクト GID を `.env` に反映 |
| 2 | **worker サブ** | PUT 400（layout-fix · addProject なし） | stderr 警告 · `CF=skip` · notes `担当:` で運用継続 |
| 3 | **未設定** | （400 ではない）poller `SKIP no_cf` | Asana UI または親タスク create 時に AI を設定 |

poller / `set_assignee_type_org_ops` が 400 のとき **処理は中断しない**（警告のみ）。intake 候補判定は `.env` の field GID とタスクの `custom_fields` の一致が前提。

## GID（プロジェクト別）

### `1214771428861230`（エージェント組織構築）

| 種別 | GID |
|------|-----|
| フィールド「担当種別」 | `1215082835199209` |
| enum `AI` | `1215082835199211` |
| enum `human` | `1215082835199210` |

### `1215102364986851`（poller テスト等）

| 種別 | GID |
|------|-----|
| フィールド「担当種別」 | `1215102364986855` |
| enum `AI` | `1215102364986857` |
| enum `human` | `1215102364986856` |

## org-ops が自動設定するタイミング

| CLI / 関数 | 担当種別 |
|------------|----------|
| `handoff_to_asana.py` 親タスク create / sync 更新 | `AI` |
| `handoff_to_asana.py` が新規作成する **execution 系 department 子**（エピック直下） | `AI`（addProject なし · PUT のみ） |
| `pm_assign_subtasks.py` の **PM 進行親**（`--update-parent-assignee` 対象） | `AI` |
| `pm_assign_subtasks.py` が作成する **worker サブ** | **`AI` を PUT で試行**（`addProject` なし · 失敗は警告のみ） |
| `create_approval_subtask.py` / `create_pm_review_gate.py`（【レビュー】/【承認】） | **human** |
| `create_subtask`（上記以外の汎用 helper） | **設定しない** |

### worker サブ CF（F2）

`pm_assign_subtasks` は各 worker サブ作成直後に `set_assignee_type_org_ops`（PUT のみ）を試行する。  
**layout-fix:** `addProject` は使わない（サブがプロジェクト直下に浮く）。  
API が 400 等で拒否する場合は stderr 警告 · dryrun 記録 · notes `担当:` で運用継続。

## human の設定

org-ops は **Asana ユーザー assignee API を使わない** ため、`human` は次のいずれか:

1. **org-ops CLI が `human` を自動設定** — `create_approval_subtask.py` / `create_pm_review_gate.py`（【承認】/【レビュー】= 人間が完了）
2. **人間がタスク作成時に設定** — 人間が実施するタスクを `human` に
3. Asana UI で CF を `human` に変更（assignee 変更後の整合用）
4. 将来: 専用 CLI `set_assignee_type(task, human)`（任意）

**誤解禁止:** `human` ≠「手動設定のみ」。**担当メンバーが人間であること**を示す（エージェントが承認サブ作成時も **human**）。

## 無効化

テスト・他プロジェクト向け:

```env
ASANA_ASSIGNEE_TYPE_DISABLED=true
```

## 参照

- ソース intake-asana: `1215082835252581`
- layout-fix: [`docs/verification/asana-subtask-layout-fix-dryrun.md`](../verification/asana-subtask-layout-fix-dryrun.md)
- dryrun: [`docs/verification/asana-assignee-type-field-dryrun.md`](../verification/asana-assignee-type-field-dryrun.md)
