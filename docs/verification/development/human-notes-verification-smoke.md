# human-notes verification — smoke checklist

再実行可能な smoke 手順。Epic `1215474016466868` の【4/4・検証】子に対応。

## 前提

- リポジトリルートがカレント
- `.venv` 有効 · `pip install -r tools/requirements-validate.txt` 済み

## チェックリスト

- [ ] `python tools/test_asana_notes_two_layer.py` → exit 0
- [ ] `python tools/validate_fixture_schemas.py` → exit 0 · `handoff.requester-facing-notes.v1.json` OK
- [ ] `python tools/validate_ssot_contract.py` → exit 0 · `task notes requester-facing layer`
- [ ] `python tools/validate_org_registry.py` → exit 0
- [ ] `docs/verification/fixtures/development/requester-facing-notes-before-after.md` が存在
- [ ] `assemble_subtask_notes("bg","sm","dw")` の出力先頭 H2 が `## 依頼者向け`

## クイック実行（PowerShell）

```powershell
$env:PYTHONIOENCODING='utf-8'
python tools/test_asana_notes_two_layer.py
python tools/validate_fixture_schemas.py
python tools/validate_ssot_contract.py
python tools/validate_org_registry.py
```

## 参照

- `docs/verification/development/human-notes-verification-dryrun.md`
- `docs/design/agent-asana-comment-signature.md` §6.1
