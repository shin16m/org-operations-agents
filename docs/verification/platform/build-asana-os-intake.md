# Build Asana OS — Asana 起票記録

> **履歴（RETIRED · 2026-06-09）** — org-os 構築 epic 群の起票記録。本番は [chat-driven-ops.md](../../design/chat-driven-ops.md)（org-os watch 不要）。

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-07 |
| プロジェクト | `1214771428861230` |
| セクション | **build asana os** `1215086511012115`（OS 作成本流） |
| Handoff SSOT | [`docs/verification/fixtures/planning/handoff/build-asana-os/`](../../fixtures/planning/handoff/build-asana-os/) |

## エピック一覧（7 本 · 子タスク 38 件）

| Epic | 親 GID | URL |
|------|--------|-----|
| 【A1】org-os セットアップ doctor + 初回オンボーディング | `1215473523834260` | https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1215473523834260 |
| 【A2】legacy epic バックフィル + CF 同期の統合 | `1215473524444431` | https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1215473524444431 |
| 【B1】標準運用ループの固定（runner を SSOT 入口に） | `1215473595838510` | https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1215473595838510 |
| 【B2】可視化ダッシュボード + org-os queue 統合 | `1215473492047743` | https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1215473492047743 |
| 【B3】execution チェーンの信頼性 + stuck 検知 | `1215473464212013` | https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1215473464212013 |
| 【C1】org-os v1.0 — テスト・パッケージ・API 凍結 | `1215473505192236` | https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1215473505192236 |
| 【C2】org-ops 統合契約 + 外部利用ドキュメント | `1215473464419216` | https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1215473464419216 |

各親は **Task Type=Epic** · **OS State=Ready** · **Approval Required=No** で bootstrap 済み。

## 推奨着手順

A1 → A2 → B1 → (B2 ∥ B3) → C1 → C2

## 再投入

```powershell
$env:ASANA_SECTION_ID = "1215086511012115"
python skills/platform/asana-buddy/optional/handoff_to_asana.py `
  --handoff docs/verification/fixtures/planning/handoff/build-asana-os/a1-doctor-onboarding.json `
  -y --if-not-exists
```
