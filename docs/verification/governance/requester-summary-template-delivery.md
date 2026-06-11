# 依頼者サマリテンプレ — Should 未達明示 — delivery 記録

| 項目 | 内容 |
|------|------|
| 日付 | 2026-06-11 |
| 子 GID | `1215492682990997` |

## 成果物

| パス | 内容 |
|------|------|
| `docs/design/epic-completion-summary-template.md` | SSOT テンプレ |
| `skills/platform/asana-buddy/optional/comment_epic_summary.py` | `--render-template` · `--should-gaps-json` |
| `docs/verification/fixtures/governance/should-gaps-sample.json` | サンプル Should ギャップ |
| `output/governance/records/1215492682990997-epic-summary-sample.md` | dry-run 出力サンプル |

## サンプル生成

```powershell
python skills/platform/asana-buddy/optional/comment_epic_summary.py `
  --gid 1215475353160824 `
  --summary "M6 — 依頼者向けサマリ（サンプル · dry-run）" `
  --render-template `
  --should-gaps-json docs/verification/fixtures/governance/should-gaps-sample.json `
  --verify-command "python output/development/app/m6-full-ui-demo/README.md 参照後 serve.py 起動" `
  --verify-command "curl -s http://127.0.0.1:8766/api/health" `
  --next-action "AC-4 ダークモードは follow-up Epic で polish" `
  --artifact "output/development/reviews/1215475391195319-verification.json" `
  --dry-run
```
