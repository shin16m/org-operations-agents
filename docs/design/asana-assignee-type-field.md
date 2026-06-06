# Asana Agent Type カスタムフィールド — 運用 SSOT

| 版 | 1.7 |
| 日付 | 2026-05-25 |
| 旧称 | 担当種別（2026-05 まで Asana 表示名） |

## 目的

Asana プロジェクトの **Agent Type** enum CF（旧称 **担当種別**）で、タスクの **担当メンバー（assignee）が AI エージェントか人間か** を一覧で判別する。

| 値 | 意味 |
|----|------|
| **AI** | 担当メンバーが **AI エージェント**（org-ops CLI / workflow が作成・管理する実行タスク） |
| **human** | 担当メンバーが **人間**（依頼者・承認者など Asana 上で人が完了するタスク） |

**`human` は「手動で CF を触ったタスク」に限らない。** 人間が作成した AI 実行タスクは **AI**、エージェントが作成した【承認】/【レビュー】は **human**（担当=人間）を org-ops が自動設定する。

### 想定運用（設定者 × Agent Type）

| 作成者 | タスク内容 | Agent Type | 設定者 |
|--------|------------|------------|--------|
| 人間 | AI に実施させるタスク | **AI** | 人間 |
| 人間 | 人間が実施するタスク | **human** | 人間 |
| エージェント | 人の承認タスク（【レビュー】/【承認】等） | **human** | エージェント |
| エージェント | AI で実施可能なタスク | **AI** | エージェント |

`.env` で上書き可能: [`skills/platform/asana-buddy/optional/.env.example`](../../skills/platform/asana-buddy/optional/.env.example)

**プロジェクトごとに CF GID が異なる場合がある。** ただし **workspace 共有 CF** は同 workspace 内の複数プロジェクトで同 GID を返す（例: 1214771428861230 と 1215102364986851 は両方 `1215082835199209`）。切替時は [`tools/sync_assignee_type_env.py`](../../tools/sync_assignee_type_env.py) で `.env` を同期する（lookup は `Agent Type` · 旧称 `担当種別` フォールバック）。

```powershell
python tools/sync_assignee_type_env.py --project <PROJECT_GID> --dry-run
python tools/sync_assignee_type_env.py --project <PROJECT_GID> --write -y
```

### sync 強化仕様（2026-05 / v1.7）

`sync_assignee_type_env.py` の CF 検出は **lazy 拒否方式**:

1. `custom_field_settings` API で取得した全行から、`custom_field.name` が `Agent Type` / `agent type` / `担当種別` のいずれかに**完全一致**（case-insensitive）する候補をすべて収集
2. 各候補について `enum_options` に **`AI` と `human` の両方が存在** することを必須にする（不完全な候補は skip して次候補を試す）
3. 完全な候補が複数あった場合は `FIELD_NAMES` の優先順位（**Agent Type > 担当種別**）で選ぶ
4. `--dry-run` 時は観測した候補と除外理由を `[KEPT]/[SKIP]` 形式で stderr に warn 表示する（debug 性向上）
5. 完全な候補が 0 件の場合は、観測候補一覧つきの ValueError を投げる

**背景:** `approval-flow E2E ドライラン` で同名の別 field（標準 assignee 関連等）に誤マッチして project-private GID を返す事象が発生したため、name 一致だけでは不十分という前提で書き換えた（[`docs/verification/platform/approval-flow-e2e-dryrun.md`](../verification/platform/approval-flow-e2e-dryrun.md) §6 を参照）。

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
| フィールド「Agent Type」（旧 担当種別） | `1215082835199209` |
| enum `AI` | `1215082835199211` |
| enum `human` | `1215082835199210` |

### `1215102364986851`（poller テスト等 — workspace 共有 CF）

| 種別 | GID |
|------|-----|
| フィールド「Agent Type」（旧 担当種別） | `1215082835199209` |
| enum `AI` | `1215082835199211` |
| enum `human` | `1215082835199210` |

> 同 workspace 内では Agent Type CF が共有されるため `1214771428861230` と同 GID。`sync_assignee_type_env.py` v1.7 で正しく検出されることを確認済み（[delivery](../verification/platform/sync-assignee-type-fix-delivery.md)）。

## org-ops が自動設定するタイミング

| CLI / 関数 | Agent Type |
|------------|------------|
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
- agent type リネームエピック: `1215089211594147`
- layout-fix: [`docs/verification/platform/asana-subtask-layout-fix-dryrun.md`](../verification/platform/asana-subtask-layout-fix-dryrun.md)
- dryrun: [`docs/verification/platform/asana-assignee-type-field-dryrun.md`](../verification/platform/asana-assignee-type-field-dryrun.md)
