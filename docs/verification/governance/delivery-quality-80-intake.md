# 納品完成度 50%→80% — Asana 起票記録

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-08 |
| プロジェクト | `1214771428861230`（エージェント組織構築） |
| セクション | **組織構築** `1215082835252574` |
| Handoff SSOT | [`docs/verification/fixtures/planning/handoff/delivery-quality-80.json`](../../fixtures/planning/handoff/delivery-quality-80.json) |

## 親エピック

| 項目 | 値 |
|------|-----|
| GID | `1215474826616152` |
| URL | https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1215474826616152 |
| Task Type | Epic |
| OS State | Ready |

## 子タスク（Execution Order 順）

| 順 | GID | タイトル | department |
|----|-----|----------|------------|
| 1 | `1215474835681087` | 完成度ギャップ監査 + 80% 定義の SSOT 化 | governance |
| 2 | `1215474834912811` | 受け入れ基準テンプレ + requirements-writer / dev-reviewer ゲート | governance |
| 3 | `1215474876660449` | tech-designer 実行契約 + design review ゲート | governance |
| 4 | `1215474826414177` | developer smoke 提出 + code review ゲート | governance |
| 5 | `1215474835658413` | VerificationResult v1.1 + qa-verifier evidence 必須 | governance |
| 6 | `1215474825767192` | pm_intake_gate 拡張 + fix R3 エスカレーション | development |
| 7 | `1215474835572118` | assign plan 全例 + verification fixture 更新 | governance |
| 8 | `1215474914455315` | UX 操作シナリオ Must 化 + ux-reviewer 拡張 | governance |
| 9 | `1215474835673597` | fix dispatch コンテキスト引き継ぎ | development |
| 10 | `1215491192881849` | DashboardBundle / fixture 方針 + 接続 AC 標準化 | governance |
| 11 | `1215474835630534` | delivery-quality smoke + 良悪例 fixture | governance |

Asana dependency は Handoff 配列順（1→2→…→11）で設定済み。

## 再投入

```powershell
$env:ASANA_SECTION_ID = "1215082835252574"
$env:ASANA_PROJECT_ID = "1214771428861230"
python skills/platform/asana-buddy/optional/handoff_to_asana.py `
  --handoff docs/verification/fixtures/planning/handoff/delivery-quality-80.json `
  -y --if-not-exists
```

## 着手

`org-ops-watch` 実行中なら Execution Order 1（governance 子）から自動 dispatch。手動の場合は task-dispatcher → governance-pm。

## 完了（2026-06-08）

- 和久桶 dispatch · 人間承認 opt-out
- 子 11 件 + 親 Epic 完了 · OS State=Done
- SSOT 実装: `docs/design/delivery-completion-standard.md` 他（Epic コメント参照）
- **follow-up:** 子 6 `pm_intake_gate.py` ツール拡張 · `pm_emit_worker_prompt.py` fix コンテキスト自動注入
