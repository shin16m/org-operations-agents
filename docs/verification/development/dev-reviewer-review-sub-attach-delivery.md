# dev-reviewer review サブ md 自動 attach — delivery 記録

| 項目 | 内容 |
|------|------|
| 実施 | 2026-06-05 |
| 親エピック GID | `1215435776639728` |
| 開発子 GID | `1215435778230658` |
| ソース intake | `1215429714465881` |
| Handoff | `output/planning/handoff/handoff.dev-reviewer-review-sub-md-attach.json` |

## 課題

worker サブへの md attach は必須化済み（`dev-md-artifacts-asana-attach`）だが、dev-reviewer の **review サブ**に同一 md が無いと初回 kick が `io_contract` failed になる。

## 本体変更

| ファイル | 内容 |
|----------|------|
| `tools/resolve_dev_review_sub.py` | PM 子 + `review_kind` から dev-reviewer review サブ GID を解決 |
| `skills/platform/asana-buddy/optional/attach_task_files.py` | `--also-gid` · `--skip-if-present` |
| `skills/development/requirements-writer/SKILL.md` | worker + review サブへの伝播手順 |
| `skills/development/dev-reviewer/SKILL.md` | attach 確認を **review サブ**基準に変更 |
| `skills/development/product-manager/SKILL.md` | PM complete 前に worker + review `--list` |
| `docs/design/development-delivery-io.md` | I/O 表更新 |

## 検証

```powershell
python tools/resolve_dev_review_sub.py --parent 1215435778230658 --review-kind requirements
python skills/platform/asana-buddy/optional/attach_task_files.py --gid 1215435795725360 --list
python skills/platform/asana-buddy/optional/attach_task_files.py --gid 1215435780328983 --list
python tools/validate_org_registry.py
python tools/validate_ssot_contract.py
```

## サブ GID（本インスタンス）

| 用途 | GID |
|------|-----|
| 要件 review | `1215435780328983` |
| mismatch review | `1215435795929961` |
| requirements worker | `1215435795725360` |
| as-built worker | `1215435833495085` |

## 教訓

- review サブは dev-reviewer が dispatch される **当該サブ** — worker サブのみ attach では io_contract 再発
- `--also-gid` + `--skip-if-present` で冪等 propagate を SKILL 化
