# org-os — リリース手順

パッケージ版 SSOT: [`pyproject.toml`](pyproject.toml) · 変更履歴: [`CHANGELOG.md`](CHANGELOG.md)

## 1. バージョン bump

[Semantic Versioning](https://semver.org/) に従う（方針: [`org-os-product-io.md`](../../docs/design/org-os-product-io.md) §10）。

| 変更種別 | bump |
|----------|------|
| syscall / queue 破壊的変更 | **MAJOR** |
| 後方互換機能追加 | MINOR |
| バグ修正のみ | PATCH |

1. `pyproject.toml` の `version`
2. `src/org_os/__init__.py` の `__version__`
3. `CHANGELOG.md` に日付付きセクション

## 2. リリース前チェック

```powershell
cd products/org-os
pip install -e ".[dev]"
pytest tests -q
cd ../..
python tools/test_org_os_integration.py -v
python tools/validate_ssot_contract.py
python tools/org_os.py doctor
```

CI: `.github/workflows/validate.yml` の `org-os` job が green であること。

## 3. モノレポ wrapper 互換

`tools/org_os.py` はリポジトリ内ラッパー。リリース後に必ず確認:

```powershell
python tools/org_os.py doctor
python tools/org_os.py queue ready --project <PROJECT_GID> --json
```

`pip install -e products/org-os` 済み環境では `org-os` コマンドと同等であること。

## 4. org-ops 統合

org-operations-agents 本体は **org-os を外部プロダクト**として import する。epic CF 書込みは `org_os.syscall` のみ（`tools/validate_ssot_contract.py` が `tools/*.py` の直 PUT を検出）。

依存一覧: `org-os-product-io.md` §7 · §7.1

## 5. 別リポジトリ分離（★5 · 本 epic スコープ外）

org-os の独立 Git リポジトリ化 · PyPI 公開は **★5** で計画する。本 RELEASE はモノレポ内 `products/org-os/` 配布を前提とする。

★5 着手時のチェックリスト（参考）:

- `products/org-os/` を subtree split または新 repo へ移動
- `tools/org_os.py` を thin wrapper または削除し `pip install org-os` を必須化
- CI を org-os 専用 workflow に分離
- CONSUMER.md の clone URL を更新

## 6. タグ（任意）

モノレポ内リリース記録:

```powershell
git tag org-os-v1.0.0
```

PyPI 公開時は別手順（★5）で `twine upload` 等を追加する。
