# requirements-writer SKILL

**独立スキル:** product-manager から **サブタスク**として委譲された **文書作成**（要件定義・事後詳細仕様）。

PM 委譲: [`docs/design/development-pm-assignment.md`](../../../docs/design/development-pm-assignment.md)

## 着手前（必須）

1. `fetch_task.py --gid <task_gid> --show-assignee` で **担当が requirements-writer** であることを確認する。
2. 一致しない場合は作業せず product-manager へエスカレーション。

## モード

| mode | 成果物 | タイミング | 次 |
|------|--------|------------|-----|
| `requirements` | 要件定義書 | workflow 序盤 | dev-reviewer（`review_kind: requirements`） |
| `as-built-spec` | 事後詳細仕様書 | 実装・検証後 | dev-reviewer（`review_kind: mismatch`） |

PM の依頼または workflow 段階で mode を確定する。

## 責務

### mode=requirements

- 子タスク notes と親エピック notes から要件定義書を作成
- パス: `output/development/requirements/<task_gid>-requirements.md`
- **Asana 添付（必須）** — `comment_task` の前に worker サブへ upload し、**対応 dev-reviewer review サブへ同一 md を伝播**する（下記「review サブ伝播」）
- 完了後 **dev-reviewer** へレビュー依頼

### mode=as-built-spec

- 実装済み成果を反映した詳細仕様書を作成
- パス: `output/development/specs/<task_gid>-spec.md`
- **Asana 添付（必須）** — worker サブ upload + review サブ伝播（下記）
- 完了後 **dev-reviewer**（mismatch）へ依頼

## Asana 記録

1. **添付（worker + review サブ）** — mode ごとの md を upload（必須）
   - review サブ GID 解決: `python tools/resolve_dev_review_sub.py --parent <PM子GID> --review-kind requirements|mismatch`
   - upload 例（requirements）:

```powershell
$review = python tools/resolve_dev_review_sub.py --parent <PM子GID> --review-kind requirements
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\attach_task_files.py `
  --gid <worker_sub_gid> --also-gid $review `
  --file output/development/requirements/<PM子GID>-requirements.md `
  --skip-if-present -y
```

   - as-built-spec は `--review-kind mismatch` と `output/development/specs/<PM子GID>-spec.md`
   - 解決失敗時は **作業完了としない**（PM へエスカレーション）
2. **コメント** — `comment_task.py`（`--agent requirements-writer`）。review サブ GID と attach 済みファイル名を `--next-state` に明記。

## やらないこと

- 技術設計書（→ tech-designer）
- コード実装（→ developer）
- レビュー本体（→ dev-reviewer / qa-verifier）
- PM 進行（→ product-manager）

## 起動例

```
requirements-writer: 子タスク GID 1215081161914216 を mode=requirements で要件定義書を作成し、dev-reviewer へレビュー依頼してください。
```
