# 納品品質 follow-up — Asana 起票記録

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-08 |
| プロジェクト | `1214771428861230`（エージェント組織構築） |
| セクション | **組織構築** `1215082835252574` |
| Handoff SSOT | [`docs/verification/fixtures/planning/handoff/delivery-quality-followup-tools.json`](../../fixtures/planning/handoff/delivery-quality-followup-tools.json) |

## Step 1 — バックログ整理

休眠 intake **16 件**を superseded としてクローズ（重複 `[retro]` · 完了済み doc-only · Phase 2 へ移管分）。

## 親エピック

| 項目 | 値 |
|------|-----|
| GID | `1215475080199865` |
| URL | https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1215475080199865 |
| Task Type | Epic |
| OS State | Ready |

## 子タスク（Execution Order 順）

| 順 | GID | タイトル | department |
|----|-----|----------|------------|
| 1 | `1215475096499996` | pm_intake_gate 拡張 — AC 表・実行契約チェック | development |
| 2 | `1215475097064096` | pm_create_fix_subtask — R3 エスカレーション + 自動 kick 停止 | development |
| 3 | `1215475209897115` | pm_emit_worker_prompt — fix サブ向けコンテキスト自動注入 | development |

Asana dependency は Handoff 配列順（1→2→3）で設定済み。

## 再投入

```powershell
$env:ASANA_SECTION_ID = "1215082835252574"
$env:ASANA_PROJECT_ID = "1214771428861230"
python skills/platform/asana-buddy/optional/handoff_to_asana.py `
  --handoff docs/verification/fixtures/planning/handoff/delivery-quality-followup-tools.json `
  -y --if-not-exists
```

## 着手

`org-ops-watch` 実行中なら Execution Order 1（development 子）から自動 dispatch。前 Epic `1215474826616152` follow-up。
