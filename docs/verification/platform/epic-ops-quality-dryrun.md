# エピック運用品質改善 — dryrun 記録

| エピック | `1215085908251056` |
| governance 子 | `1215086041646050` |
| audit 子 | `1215085955257649` |
| ソース | `1215082835252613` |
| 実施日 | 2026-05-24 |

## 背景（フィードバック）

| # | 問題 | 対応 |
|---|------|------|
| 1 | bootstrap 時に重複親 `1215085907629201` | `handoff_to_asana.py` section 失敗時も subtasks 継続 + recovery_hint |
| 2 | ワーカー署名コメント欠如 | PM assignment + comment SSOT に `--agent` 規則追記 |
| 3 | PM 代行 | cursor rule / orchestrator SKILL 強化 |
| 4 | エピック完了サマリなし | `comment_epic_summary.py` 新規 |

## validate

```powershell
python tools/validate_org_registry.py
python tools/validate_ssot_contract.py
python tools/validate_fixture_schemas.py
python tools/check_new_department.py --all
```

## 重複タスク `1215085907629201` のクリーンアップ（手動）

bootstrap create モード再実行で残った孤児親。自動削除はスコープ外。

1. Asana でタイトル・子の有無を確認（本 epic `1215085908251056` と混同しない）
2. 子が無ければ notes に `duplicate of 1215086192458137 bootstrap retry` を追記
3. `complete_task.py --gid 1215085907629201 -y` でアーカイブ相当

## 変更ファイル

- `skills/platform/asana-buddy/optional/handoff_to_asana.py`
- `skills/platform/asana-buddy/optional/comment_epic_summary.py`（新規）
- `skills/platform/workflow-orchestrator/SKILL.md`
- `.cursor/rules/workflow-intake-required.mdc`
- `docs/design/agent-asana-comment-signature.md`
- `docs/design/*-pm-assignment.md`（5 件）
- `tools/validate_ssot_contract.py`

## 参照

- 対象フィードバック epic: `1215086192458137`
- [`asana-comment-detail-delivery.md`](asana-comment-detail-delivery.md)
