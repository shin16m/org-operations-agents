# developer SKILL

**独立スキル:** PM から委譲された **実装・修正**。

## 責務

1. 要件定義書（`requirements-doc`）を読み実装する
2. 完了後 **reviewer**（`review_kind: code`）へレビュー依頼
3. レビュー OK → **reviewer**（`review_kind: verification`）へ動作検証依頼
4. 検証 OK → **product-manager** へ開発完了報告
5. PM からの修正依頼（ミスマッチ `fix_target: code` 等）に対応
6. 実装・修正が `done_when` を満たしたら **署名付きコメント**を投稿してから **product-manager** へ報告

```powershell
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\comment_task.py --gid <子GID> --agent developer --skill skills/developer/SKILL.md --summary "実装完了" --body-file .\comment-body.md -y
```

- PM が `complete_task.py` を実行するまで Asana タスクは未完了のまま
- 契約: [`docs/design/agent-asana-comment-signature.md`](../../docs/design/agent-asana-comment-signature.md)

## やらないこと

- 要件定義書・詳細仕様の主作成（→ doc-writer）
- PM の進行管理

## 起動例

```
developer: 要件定義書 docs/requirements/1214877045257081-requirements.md に従い実装し、reviewer へコードレビューを依頼してください。
```
