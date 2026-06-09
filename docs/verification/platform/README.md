# platform — 統括グループ検証索引

**本番 SSOT:** [`docs/design/chat-driven-ops.md`](../../design/chat-driven-ops.md)（和久桶さんチャット入口 · Asana タスク運用継続 · **自動化廃止**）

## 現行（active）

| ファイル | 種別 | 内容 |
|----------|------|------|
| [`chat-driven-ops-dryrun.md`](chat-driven-ops-dryrun.md) | dryrun | **チャット入口移行** — validate + 手順整合の実行記録 |
| [`chat-driven-ops-migration-handoff.md`](chat-driven-ops-migration-handoff.md) | handoff | Asana 自動化廃止セッション引継ぎ |
| [`orchestrator-intake-dryrun.md`](orchestrator-intake-dryrun.md) | dryrun | intake → bootstrap → dispatch（v3/v6 手順） |
| [`org-dispatch-pm-smoke.md`](org-dispatch-pm-smoke.md) | smoke | dispatch → PM 配賦 |
| [`agent-comment-smoke.md`](agent-comment-smoke.md) | smoke | 署名付き comment / complete |
| [`approval-flow-e2e-dryrun.md`](approval-flow-e2e-dryrun.md) | dryrun | 承認フロー E2E（チャット gate 含む） |
| [`asana-comment-detail-delivery.md`](asana-comment-detail-delivery.md) | delivery | PM 代行事後補完 |
| [`pm-worker-separation-delivery.md`](pm-worker-separation-delivery.md) | delivery | PM / ワーカー分離 |
| [`b3-pm-worker-complete-bridge-dryrun.md`](b3-pm-worker-complete-bridge-dryrun.md) | dryrun | complete bridge |
| [`epic-retrospective-intake-dryrun.md`](epic-retrospective-intake-dryrun.md) | dryrun | レトロ intake |
| [`milestone-readiness-ms3-dryrun.md`](milestone-readiness-ms3-dryrun.md) | dryrun | MS3 readiness |
| [`m5.1-retro-loop-followup-delivery.md`](m5.1-retro-loop-followup-delivery.md) | delivery | M5.1 レトロ follow-up |

→ その他 Asana タスク運用・kick 修正・コメント改善系: 本フォルダ内で **RETIRED 注記なし** のファイル

## 履歴（Asana 自動化 / org-os · RETIRED）

冒頭に `> **履歴（RETIRED · 2026-06-09）**` があるファイル。watch / poller / runner / org-os watch 連携の検証ログ。

| 代表例 | 内容 |
|--------|------|
| [`asana-driven-ops-dryrun.md`](asana-driven-ops-dryrun.md) | Phase 1 自動化 |
| [`org-os-kernel-e2e-dryrun.md`](org-os-kernel-e2e-dryrun.md) | org-os kernel E2E |
| [`wakuoke-auto-kick-delivery.md`](wakuoke-auto-kick-delivery.md) | 自動 kick |
| [`runner-resume-approval-helper-delivery.md`](runner-resume-approval-helper-delivery.md) | runner + approval helper |

**一覧:** `grep -l "履歴（RETIRED" docs/verification/platform/*.md`

削除済みツール索引: [`tools/_retired/README.md`](../../../tools/_retired/README.md) · org-os パッケージ: [`products/_retired/README.md`](../../../products/_retired/README.md)

## 関連

- 手順 SSOT: [`docs/e2e/default-workflow.md`](../../e2e/default-workflow.md)
- 全 verification 索引: [`docs/verification/README.md`](../README.md)
