# intake-asana planning gate 統一 — delivery

| 項目 | 内容 |
|------|------|
| 親 epic | `1215131549360577` |
| intake（close 済） | `1215131307711213` |
| 実施日 | 2026-05-26 |
| プロジェクト | `1214771428861230`（本番） |

## 目的

intake-asana でも planning gate を **Asana 【承認】+ `--record-wait` + A/B/C** のみとし、チャット「承認待ち」禁止を SKILL / SSOT に反映する。

## planning gate 実演（本 epic）

| 段階 | 結果 |
|------|------|
| A `create_approval_subtask` | ✅ 親 Waiting · Approval Required=Yes · sub `1215131549154648` |
| 人間 Asana complete | ✅ |
| B `approval_helper` | ✅ APPROVED |
| C `wakuoke_resume_scan` | ✅ RESUME `1215131549360577` |
| `handoff_to_asana` | ✅ execution 子 3 件 sync |

## 成果物

| 種別 | パス |
|------|------|
| Handoff | `output/planning/handoff/handoff.intake-asana-planning-gate.json` |
| development | SKILL 3 本 · `output/development/requirements/1215131832179152-requirements.md` |
| governance | `asana-driven-ops.md` v1.4 · `planning-gate-vs-pm-review-gate.md` v1.2 · `workflow-io-contract.md` |
| audit | `output/audit/reports/1215131583361641-consistency.json` |

## validate（audit）

| スクリプト | exit |
|-----------|------|
| validate_org_registry.py | 0 |
| validate_fixture_schemas.py | 0 |
| validate_ssot_contract.py | 0 |

## 今後の課題（org-os · 依頼者指摘）

**現象:** PM review gate（【レビュー】）や一部 gate 待ち中、**親 epic の `OS State` が `Running` のまま**（`output/platform/sessions/` のみ WAIT）。`wait_list` / poller から gate 待ち epic を OS CF で判別できない。

**期待:** `--record-wait` 時に **親 epic GID** へ `syscall.suspend(..., "Human Review")`（planning 【承認】は `Approval`）。gate complete → `syscall.resume`。

**SSOT 記録:** [`asana-driven-ops.md`](../design/asana-driven-ops.md) §org-os · [`planning-gate-vs-pm-review-gate.md`](../design/planning-gate-vs-pm-review-gate.md) §org-os

**推奨:** 別 Intake epic（tools: `create_pm_review_gate` · `asana_ops_poller --record-wait` · org-os syscall 拡張）

## 関連

- 中止 epic（チャット gate）: `1215131537365881`
- 本 epic 企画子: `1215131320003737`（complete）
