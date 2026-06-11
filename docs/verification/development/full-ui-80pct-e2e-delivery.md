# full-ui 代表 E2E 80% 実証 — delivery 記録

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-11 |
| ロードマップ子 GID | `1215475391195319` |
| 代表 Epic 参照 | UX→dev dryrun `1215466257349499` / dev 子 `1215465981793109` |
| デモアプリ | `output/development/app/m6-full-ui-demo/` |

## 80% 達成確認

| 条件 | 結果 |
|------|------|
| README 起動 | ○ `output/development/app/m6-full-ui-demo/README.md` |
| Must AC 100% | ○ AC-1 · AC-2 |
| Should ≥60% | ○ 2/3（AC-3 · AC-5 pass · AC-4 未達） |
| smoke.md | ○ `output/development/smoke/1215475391195319.md` |
| qa verification | ○ `output/development/reviews/1215475391195319-verification.json` passed_with_notes |
| dev-reviewer | ○ `1215475391195319-requirements-review.json` |

## 検証（再実行）

```powershell
cd E:\data\document\sourse\org-operations-agents
# terminal 1
python output/development/app/m6-full-ui-demo/serve.py
# terminal 2
curl -s http://127.0.0.1:8766/api/health
curl -s http://127.0.0.1:8766/ | findstr "80%"
curl -s -o NUL -w "%{http_code}" http://127.0.0.1:8766/api/error-demo
python tools/aggregate_delivery_kpi.py --json
```

## 依頼者確認

Epic 親 `1215475353160824` にサマリコメント投稿済み（task 6 テンプレ `--render-template` サンプル連動可）。
