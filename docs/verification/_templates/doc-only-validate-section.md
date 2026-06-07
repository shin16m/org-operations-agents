# doc-only validate 節テンプレート（コピー用）

> **使い方:** 本ファイルを doc-only dryrun / delivery / smoke にコピーし、`{parent_gid}` `{実施日}` 等のプレースホルダを置換する。  
> SSOT: [`docs/verification/README.md`](../README.md) · 既定表は README と整合すること。

## validate（doc-only）

### 実行コマンド

```powershell
cd E:\data\document\sourse\org-operations-agents
$env:PYTHONIOENCODING='utf-8'
python tools/validate_org_registry.py
python tools/validate_fixture_schemas.py
python tools/validate_ssot_contract.py
```

### 実行結果

| コマンド | 判定 | exit | 理由 |
|----------|------|------|------|
| `validate_org_registry.py` | 実行 | 0 | registry 整合（doc-only · メタ doc のみ変更） |
| `validate_fixture_schemas.py` | skip | - | fixture 未変更のため skip（`git diff` で fixtures/ 差分なし） |
| `validate_ssot_contract.py` | 実行 | 0 | SSOT 契約検証 pass |

### skip 理由（該当時）

- **`validate_fixture_schemas.py`:** fixture JSON を変更していない doc-only のため skip。変更範囲は `docs/` のみ。

---

## doc-only 既定表（参照）

| コマンド | doc-only 既定 | skip 許容例 |
|----------|---------------|-------------|
| `validate_org_registry.py` | **実行** | registry / workflow YAML 未変更かつ事前確認済み |
| `validate_fixture_schemas.py` | fixture 変更時のみ | fixture 未変更の doc-only |
| `validate_ssot_contract.py` | **実行** | SSOT 契約未変更かつ事前確認済み（稀） |
