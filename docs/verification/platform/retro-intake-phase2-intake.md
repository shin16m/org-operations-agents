# レトロ / intake 自動化 Phase 2 — Asana 起票記録

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-08 |
| プロジェクト | `1214771428861230`（エージェント組織構築） |
| セクション | **組織構築** `1215082835252574` |
| Handoff SSOT | [`docs/verification/fixtures/planning/handoff/retro-intake-phase2.json`](../../fixtures/planning/handoff/retro-intake-phase2.json) |

## 親エピック

| 項目 | 値 |
|------|-----|
| GID | `1215475084856660` |
| URL | https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1215475084856660 |
| Task Type | Epic |
| OS State | Ready |

## 子タスク（Execution Order 順）

| 順 | GID | タイトル | department |
|----|-----|----------|------------|
| 1 | `1215491517102919` | assign plan JSON への [retro] サブ自動同梱 | development |
| 2 | `1215475085127976` | aggregate_epic_retrospective に --parent サブタスクフィルタ | development |
| 3 | `1215475142748815` | Epic complete 前 check — retro gate 未作成なら WARN | development |
| 4 | `1215491557624250` | run_all_teams_dryrun.py を audit チーム対応に拡張 | development |
| 5 | `1215475097082132` | default.yaml に suspend/resume 段階を追加 | development |
| 6 | `1215475080245914` | レトロスペクティブ完了前に依頼者意見を必須化 | development |
| 7 | `1215475209626800` | Asana stories から依頼者コメント自動パース | development |
| 8 | `1215475142717078` | dashboard Ready 件数表示 + execution 開発子 pm_assign lite 初手必須 | development |

Asana dependency は Handoff 配列順（1→…→8）で設定済み。

## 再投入

```powershell
$env:ASANA_SECTION_ID = "1215082835252574"
$env:ASANA_PROJECT_ID = "1214771428861230"
python skills/platform/asana-buddy/optional/handoff_to_asana.py `
  --handoff docs/verification/fixtures/planning/handoff/retro-intake-phase2.json `
  -y --if-not-exists
```

## 着手順

follow-up Epic（`1215475080199865`）完了後、または並行不可の場合は **follow-up を先**（納品 enforcement が優先）。同一 watch 下では Execution Order 1 から。

## 完了（2026-06-08）

- 子 8 件 + 親 Epic 完了
- delivery 記録: [`retro-intake-phase2-delivery.md`](retro-intake-phase2-delivery.md)
- ロードマップ M5 トラッカー `1215475369302645` complete
