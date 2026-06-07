# Build Asana OS — Handoff fixtures

**本流セクション:** Asana project `1214771428861230` · section **build asana os** (`1215086511012115`)

セットアップ UX → 自動運用 → プロダクト化を ★4 まで上げる 7 エピックの Handoff SSOT。

| Epic | Handoff | 領域 |
|------|---------|------|
| A1 | [`a1-doctor-onboarding.json`](a1-doctor-onboarding.json) | セットアップ UX |
| A2 | [`a2-backfill-sync.json`](a2-backfill-sync.json) | セットアップ UX |
| B1 | [`b1-runner-ssot.json`](b1-runner-ssot.json) | 自動運用 |
| B2 | [`b2-dashboard-queue.json`](b2-dashboard-queue.json) | 自動運用 |
| B3 | [`b3-execution-reliability.json`](b3-execution-reliability.json) | 自動運用 |
| C1 | [`c1-org-os-v1.json`](c1-org-os-v1.json) | プロダクト化 |
| C2 | [`c2-integration-contract.json`](c2-integration-contract.json) | プロダクト化 |

## Asana 投入

```powershell
$env:ASANA_SECTION_ID = "1215086511012115"
$handoffs = @(
  "a1-doctor-onboarding.json",
  "a2-backfill-sync.json",
  "b1-runner-ssot.json",
  "b2-dashboard-queue.json",
  "b3-execution-reliability.json",
  "c1-org-os-v1.json",
  "c2-integration-contract.json"
)
foreach ($h in $handoffs) {
  python skills/platform/asana-buddy/optional/handoff_to_asana.py `
    --handoff "docs/verification/fixtures/planning/handoff/build-asana-os/$h" -y
}
```

## 推奨順序

A1 → A2 → B1 → (B2 ∥ B3) → C1 → C2

## Asana 起票済み（2026-06-07）

| Epic | 親 GID |
|------|--------|
| A1 | `1215473523834260` |
| A2 | `1215473524444431` |
| B1 | `1215473595838510` |
| B2 | `1215473492047743` |
| B3 | `1215473464212013` |
| C1 | `1215473505192236` |
| C2 | `1215473464419216` |

記録: [`docs/verification/platform/build-asana-os-intake.md`](../../../../platform/build-asana-os-intake.md)
