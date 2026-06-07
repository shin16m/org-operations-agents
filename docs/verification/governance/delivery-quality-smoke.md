# delivery-quality smoke — 納品完成度 SSOT 回帰

Epic: `1215474826616152` · 再実行可能チェックリスト

## validate

```powershell
cd E:\data\document\sourse\org-operations-agents
$env:PYTHONIOENCODING='utf-8'
python tools/validate_org_registry.py
python tools/validate_fixture_schemas.py
python tools/validate_ssot_contract.py
```

| コマンド | 期待 |
|----------|------|
| validate_org_registry.py | exit 0 |
| validate_fixture_schemas.py | exit 0（verification v1.1 fixture 含む） |
| validate_ssot_contract.py | exit 0 |

## SSOT 存在確認

| パス | 内容 |
|------|------|
| docs/design/delivery-completion-standard.md | 80% 定義 |
| docs/design/acceptance-criteria-template.md | AC テンプレ |
| docs/design/developer-smoke-template.md | smoke テンプレ |
| skills/development/qa-verifier/schemas/verification-result.v1.schema.json | evidence + schema 1.1 |
| docs/design/pm-review-rework-ssot.md | R3 エスカレーション節 |

## fixture 例

| 種別 | パス |
|------|------|
| 良い例 verification | docs/verification/fixtures/development/verification-result-80pct-good.v1.json |
| 悪い例 verification | docs/verification/fixtures/development/verification-result-50pct-bad.v1.json |
