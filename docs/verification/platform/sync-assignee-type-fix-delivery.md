# sync_assignee_type_env CF 誤マッチ修正 — delivery

| 項目 | 値 |
|------|------|
| 実施日 | 2026-05-25 |
| 親 epic | `1215089847307763` |
| Intake | `1215089813716206`（close 済） |
| 発見元 | [`approval-flow-e2e-dryrun.md`](approval-flow-e2e-dryrun.md) §6 |
| profile | lite（tools 1 本 + SSOT 1 本） |

## 背景

approval-flow A+B+C の E2E ドライラン中、新プロジェクト `1215102364986851` で `tools/sync_assignee_type_env.py --dry-run` を実行したところ、**workspace 共有の Agent Type CF（GID=`1215082835199209`）ではなく project-private な別 field（cp932 文字化けで `field=担当者` と表示）に誤マッチ**し GID `1215102364986855` を返した。

その値で `.env` を更新後、`set_assignee_type` 呼出が `400 Custom field with ID 1215102364986855 is not on given object` で失敗。

## 修正

### `tools/sync_assignee_type_env.py`

`fetch_assignee_type_gids` を **lazy 拒否方式** に書き換え:

| 旧 | 新 (v1.7) |
|----|----|
| 最初に name match した CF を即 return | 全候補を走査し、`AI` と `human` 両 enum を持つものだけ採用 |
| enum 不完全なら ValueError | enum 不完全な候補は skip し、次候補を試す |
| 観測候補非表示 | `--dry-run` 時に `[KEPT]/[SKIP] field=... gid=... reason` を stderr に warn 表示 |
| 1 候補前提 | 複数候補が完全な場合は `FIELD_NAMES` 優先順位（Agent Type > 担当種別） |

### `docs/design/asana-assignee-type-field.md`

- 版 v1.6 → **v1.7**
- 「sync 強化仕様（2026-05 / v1.7）」セクション追加（lazy 拒否方式の仕様を SSOT 化）
- プロジェクト `1215102364986851` の GID 表を **workspace 共有 GID `1215082835199209`** に訂正（旧記載の `1215102364986855` は誤検出値）

## 動作確認

```
> python tools/sync_assignee_type_env.py --project 1215102364986851 --dry-run
OK  project=1215102364986851  field=Agent Type
  ASANA_PROJECT_ID=1215102364986851
  ASANA_ASSIGNEE_TYPE_FIELD_GID=1215082835199209
  ASANA_ASSIGNEE_TYPE_AI_GID=1215082835199211
  ASANA_ASSIGNEE_TYPE_HUMAN_GID=1215082835199210
  [KEPT] field='Agent Type' gid=1215082835199209 ok

> python tools/sync_assignee_type_env.py --project 1214771428861230 --dry-run
OK  project=1214771428861230  field=Agent Type
  ASANA_PROJECT_ID=1214771428861230
  ASANA_ASSIGNEE_TYPE_FIELD_GID=1215082835199209
  ASANA_ASSIGNEE_TYPE_AI_GID=1215082835199211
  ASANA_ASSIGNEE_TYPE_HUMAN_GID=1215082835199210
  [KEPT] field='Agent Type' gid=1215082835199209 ok
```

両プロジェクトで正解 GID が返され、regression がないことを確認。

## スコープ外

- `sync_task_type_env.py` / `sync_org_os_cf_env.py` への横展開
  - 現状は実害が観測されていないが、同様の lazy 拒否方式で書き換えるかは別 Intake で判断
- workspace API 直叩きへの切替
- 既存 `.env` の自動補正（手動で書換済）

## 関連リンク

- 設計 SSOT: [`docs/design/asana-assignee-type-field.md`](../design/asana-assignee-type-field.md)
- 発見元 E2E: [`approval-flow-e2e-dryrun.md`](approval-flow-e2e-dryrun.md)
- 親 epic: https://app.asana.com/1/1214766054680431/project/1215102364986851/task/1215089847307763
