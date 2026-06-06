# WinError 10038 kick fix — delivery 記録

| 項目 | 内容 |
|------|------|
| 実施 | 2026-06-04 |
| 親エピック GID | `1215422352722327` |
| ソース intake | `1215418535230648` |
| Handoff | `output/planning/handoff/handoff.winerror-10038-kick-fix.json` |

## 子タスク

| # | GID | department | 状態 |
|---|-----|------------|------|
| 1/5 企画 | `1215423802103358` | planning | complete |
| 2/5 開発 | `1215422685226987` | development | complete |
| 3/5 開発 | `1215422854152277` | development | complete |
| 4/5 組織改善 | `1215422371707253` | governance | complete |
| 5/5 監査 | `1215422371826023` | audit | complete |

## 本体変更

| ファイル | 内容 |
|----------|------|
| `tools/cursor_sdk_kick.py` | 共有 kick · Windows 隔離 subprocess · cloud runtime 分岐 |
| `tools/cursor_epic_dispatch.py` | `kick_prompt` 経由 |
| `tools/cursor_worker_dispatch.py` | 同上 |
| `tools/cursor_intake_dispatch.py` | 同上 |
| `tools/task_dispatcher.py` | 同上 |
| `tools/test_cursor_sdk_kick.py` | isolation / runtime unit tests |
| `docs/design/asana-driven-ops.md` | § Windows kick 隔離 · env 表 |

## 検証

```powershell
python -m unittest tools.test_cursor_sdk_kick -v
python tools/cursor_sdk_kick.py --dry-run-isolation
python tools/cursor_epic_dispatch.py --epic 1215422352722327 --mode planning --planning-child 1215423802103358 -y
python tools/validate_org_registry.py
python tools/validate_ssot_contract.py
```

## 監査結果

| 成果物 | パス | status |
|--------|------|--------|
| ConsistencyAuditReport | `output/audit/reports/1215422371826023-consistency.json` | passed |
| AuditReviewResult | `output/audit/reviews/1215422371826023-audit-review.json` | passed |

## 教訓

- **WinError 10038** — poller 子プロセス内 in-process `Agent.prompt` が原因。Windows では `--worker` 隔離が正規。
- **watch-auto epic との境界** — 1215423786532969 は検知/HINT。本 epic が実 fix。
- **CI** — Linux では isolation off。Windows 手動または `--dry-run-isolation` で確認。
