# auto kick 承認未作成 — delivery 記録

> **履歴（RETIRED · 2026-06-09）** — Asana **自動化** / org-os の検証記録。本番は [chat-driven-ops.md](../../design/chat-driven-ops.md)（和久桶チャット入口 · Asana タスク運用継続）。

| 項目 | 内容 |
|------|------|
| 実施 | 2026-06-04 |
| 親エピック GID | `1215425480034551` |
| ソース intake | `1215424511419338` |
| Handoff | `output/planning/handoff/handoff.auto-kick-approval-not-created.json` |

## 確定原因

子プロセス隔離後も worker 子内で `WinError 10038` が再発（ローカル SDK bridge 不可）。kick が落ちる限り CLI 単独では Handoff を作れず、planning 【承認】が作成されない。

## 子タスク

| # | GID | department | 状態 |
|---|-----|------------|------|
| 1/5 企画 | `1215425546882320` | planning | complete |
| 2/5 開発 | `1215425548641357` | development | complete |
| 3/5 開発 | `1215425671157263` | development | complete |
| 4/5 組織改善 | `1215425671329616` | governance | complete |
| 5/5 監査 | `1215425481417751` | audit | complete |

## 本体変更

| ファイル | 内容 |
|----------|------|
| `tools/cursor_sdk_kick.py` | `cloud_fallback_enabled` · `_attempt_kick` · local 失敗時 cloud 1 回リトライ |
| `tools/test_cursor_sdk_kick.py` | fallback 判定・cloud リトライ test（計 12） |
| `tools/test_planning_stuck.py` | stuck WARN / Done ガード回帰（3） |
| `docs/design/asana-driven-ops.md` | § local bridge 不可環境の正規運用（cloud kick） |

## 検証

```powershell
python -m unittest tools.test_cursor_sdk_kick tools.test_planning_stuck
python tools/cursor_sdk_kick.py --dry-run-isolation
python tools/validate_ssot_contract.py
python tools/validate_org_registry.py
```

## 監査結果

| 成果物 | パス | status |
|--------|------|--------|
| ConsistencyAuditReport | `output/audit/reports/1215425481417751-consistency.json` | passed |
| AuditReviewResult | `output/audit/reviews/1215425481417751-audit-review.json` | passed |

## 教訓

- 隔離（前 epic）は 10038 を解消しなかった — bridge 自体が不可な環境がある
- LLM kick が必須な工程（Handoff 生成）は、local 不可なら **cloud runtime** か **手動 planning-pm** が正規
- cloud kick は **push 済みブランチを clone** するため、未 push 変更は反映されない（運用前 push 必須）
