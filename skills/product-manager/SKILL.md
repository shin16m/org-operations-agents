# product-manager SKILL

**独立スキル:** 開発課における **子タスク 1 件**の進行管理（L3 ハブ）。

人間向け: [`README.md`](README.md) · workflow: [`workflows/development-delivery.yaml`](../../workflows/development-delivery.yaml)

## 責務

1. `fetch_task.py --gid <task_gid>` で子の notes（背景・概要・完了条件）を読む
2. 親エピック notes を文脈として参照（任意）
3. 状態に沿い委譲:
   - **doc-writer** — 要件定義書 → 詳細仕様書
   - **developer** — 実装・修正
   - **reviewer** — 各レビュー・動作検証
4. `MismatchReviewResult.fix_target == code` 時: developer へ修正依頼（doc-writer 業務は一旦完了）
5. 子の `done_when` を満たしたら **必ず** `complete_task.py` を実行してから `DeptWorkComplete` を出力する（順序固定）
6. **workflow-orchestrator** へ完了を報告

## Asana 記録（必須・順序）

```powershell
# 1. 署名付きコメント（誰が何をしたか）
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\comment_task.py --gid <子GID> --agent product-manager --skill skills/product-manager/SKILL.md --summary "子タスク完了" --body "実施内容..." -y

# 2. 完了マーク
.\.venv\Scripts\python.exe .\skills\asana-buddy\optional\complete_task.py --gid <子GID> -y
```

- 委譲先（doc-writer / developer / reviewer）も**各自の slug**で `comment_task.py` を実行してから PM に報告すること。
- **`DeptWorkComplete` を出す前に** 1 → 2 の順で実行。ローカルのみ完了は**禁止**。
- フォーマット: [`docs/design/agent-asana-comment-signature.md`](../../docs/design/agent-asana-comment-signature.md)
- 同一エピックで連続して N 件まで完了した場合:  
  `sync_handoff_epic.py --parent <親GID> --handoff <handoff.json> --complete-through N --complete-only`
- 詳細: [`docs/design/dept-work-io.md`](../../docs/design/dept-work-io.md)「Asana 完了同期」

## やらないこと

- Handoff 新規作成（→ issue-story-planner）
- ディスパッチ（→ task-dispatcher）
- 新規 `skills/<slug>/`（→ agent-creater）

## 成果物（artifact パス例）

| 種別 | 推奨パス例 |
|------|------------|
| 要件定義書 | `docs/requirements/<task_gid>-requirements.md` |
| 詳細仕様 | `docs/specs/<task_gid>-spec.md` |
| コード | リポジトリ内実装ファイル |

## 出力

完了時: `DeptWorkComplete` JSON（[`schemas/dept-work-complete.v1.schema.json`](schemas/dept-work-complete.v1.schema.json)）

## 起動例

```
product-manager として子タスク GID 1214877045257081 を進めてください。
development-delivery workflow に従い、要件定義から開始します。
```
