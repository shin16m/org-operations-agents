# kick subprocess UnicodeDecodeError — delivery 記録

| 項目 | 内容 |
|------|------|
| 実施 | 2026-06-04 |
| 親エピック GID | `1215424110092538` |
| ソース intake | `1215422942086249` |
| Handoff | `output/planning/handoff/handoff.kick-subprocess-unicode.json` |

## 子タスク

| # | GID | department | 状態 |
|---|-----|------------|------|
| 1/5 企画 | `1215424112083289` | planning | complete |
| 2/5 開発 | `1215424890574221` | development | complete |
| 3/5 開発 | `1215424199208788` | development | complete |
| 4/5 組織改善 | `1215424112176086` | governance | complete |
| 5/5 監査 | `1215424111865109` | audit | complete |

## 本体変更

| ファイル | 内容 |
|----------|------|
| `tools/cursor_sdk_kick.py` | `_kick_isolated_subprocess` に `encoding=utf-8` · `PYTHONIOENCODING` · worker stdio reconfigure |
| `tools/test_cursor_sdk_kick.py` | subprocess decode 回帰 test 2 件追加 |
| `docs/design/asana-driven-ops.md` | § Windows 文字コード |

## 検証

```powershell
python -m unittest tools.test_cursor_sdk_kick -v
python tools/cursor_sdk_kick.py --dry-run-isolation
python tools/validate_ssot_contract.py
```

## 監査結果

| 成果物 | パス | status |
|--------|------|--------|
| ConsistencyAuditReport | `output/audit/reports/1215424111865109-consistency.json` | passed |
| AuditReviewResult | `output/audit/reviews/1215424111865109-audit-review.json` | passed |

## 教訓

- WinError 10038 隔離後も **親の subprocess decode** が cp932 だと UTF-8 出力で落ちる
- poller `_run_capture` と同型の `encoding=utf-8` を kick 共有モジュールにも必須
