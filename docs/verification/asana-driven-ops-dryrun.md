# Asana ドリブン運用 — development dryrun 記録

| エピック | `1215101833446108` |
| development 子 | `1215086600091084` |
| ブランチ | `feature/asana-driven-ops` |
| 実施日 | 2026-05-24 |

## 実装

| ファイル | 内容 |
|----------|------|
| `tools/asana_ops_poller.py` | スキャン · intake trigger · WAIT/RESUME |
| `tools/check_workflow_suspend.py` | セッション gate 確認 |

## コマンド

```powershell
$env:PYTHONIOENCODING="utf-8"
python tools/asana_ops_poller.py --once --dry-run
python tools/check_workflow_suspend.py --list
python tools/validate_org_registry.py
python tools/validate_ssot_contract.py
python tools/validate_fixture_schemas.py
```

## 結果

| チェック | 結果 |
|----------|------|
| poller dry-run | exit 0 · SCAN 行出力 |
| check_workflow_suspend | exit 0 |
| validate 3 本 | OK |

## 所見

- CF 未設定 / API 400 環境では `candidates=0` · `SKIP no_cf` が多数（既知）
- 自動 bootstrap は Phase 1 スコープ外 — `--trigger-intake` は snapshot のみ

## 参照

- UX: `output/ux/specs/1215086510974424-ux-spec.html`
- 要件: `output/development/requirements/1215086600091084-requirements.md`
