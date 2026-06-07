# human-notes verification — dryrun

Epic GID: `1215474016466868`  
Verification 子 GID: `1215474028063933`

## 実行日

2026-06-08

## コマンド

```powershell
cd E:\data\document\sourse\org-operations-agents
$env:PYTHONIOENCODING='utf-8'
python tools/test_asana_notes_two_layer.py
python tools/validate_fixture_schemas.py
python tools/validate_ssot_contract.py
python tools/validate_org_registry.py
```

## 期待結果

| コマンド | exit | 備考 |
|----------|------|------|
| `test_asana_notes_two_layer.py` | 0 | assemble / validate / legacy guard |
| `validate_fixture_schemas.py` | 0 | `handoff.requester-facing-notes.v1.json` + notes-two-layer |
| `validate_ssot_contract.py` | 0 | task notes requester-facing layer contract |
| `validate_org_registry.py` | 0 | registry 整合 |

## handoff_to_asana dry-run（notes 検証）

```powershell
python skills/platform/asana-buddy/optional/handoff_to_asana.py `
  --handoff docs/verification/fixtures/platform/handoff/handoff.requester-facing-notes.v1.json `
  --dry-run
```

期待: notes 検証 pass（`--allow-legacy-notes` 不要）。

## 意図的 violation（手動確認）

`## 依頼者向け` を欠いた epic notes の Handoff を `--allow-legacy-notes` なしで投入すると exit 2。

## 参照

- `output/development/requirements/1215474028063933-requirements.md`
- `docs/verification/development/human-notes-verification-smoke.md`
