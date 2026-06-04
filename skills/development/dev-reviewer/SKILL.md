# dev-reviewer SKILL

**独立スキル:** product-manager から **サブタスク**として委譲された **静的レビュー**（文書・コード・整合）。

PM 委譲: [`docs/design/development-pm-assignment.md`](../../../docs/design/development-pm-assignment.md)

**動作検証は qa-verifier が担当**（本スキルでは行わない）。

## 着手前（必須）

1. `fetch_task.py --gid <task_gid> --show-assignee` で **担当が dev-reviewer** であることを確認する。
2. 一致しない場合は作業せず product-manager へエスカレーション。

## review_kind

| review_kind | 入力 | 出力スキーマ |
|-------------|------|--------------|
| `requirements` | 要件定義書 | DocReviewResult |
| `design` | 技術設計書 | DocReviewResult（`review_kind: design`） |
| `code` | コード変更 | CodeReviewResult |
| `mismatch` | 要件定義 + 事後詳細仕様 | MismatchReviewResult |

## Asana 添付の確認（requirements / mismatch）

`review_kind` が `requirements` または `mismatch` のとき、レビュー開始前に対象 md が **当該 worker サブに attach 済み**であることを確認する。

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\attach_task_files.py --gid <worker_sub_gid> --list
```

- `requirements`: `<gid>-requirements.md` が一覧に無ければ **failed**（attach 欠落）
- `mismatch`: `<gid>-spec.md` が無ければ **failed**
- attach 欠落時は PM へ差し戻し（worker 再 dispatch）。レビュー JSON は `status: failed` + finding に `category: io_contract`

## MismatchReviewResult

- `fix_target: document` → PM が **requirements-writer 向け修正サブ**を新規作成
- `fix_target: code` → PM が **developer 向け修正サブ**を新規作成

`status: passed*` のとき **署名コメント**（`comment_task.py --agent dev-reviewer`）を投稿して PM へ提出。  
`status: failed` も review 作業完了として PM へ提出。PM が修正サブを追加（[`pm-review-rework-ssot.md`](../../../docs/design/pm-review-rework-ssot.md)）。**完了タスクの `--undo` は行わない。**

## やらないこと

- 動作検証（→ qa-verifier）
- 企画 Handoff の plan-reviewer 代替
- 実装・文書の主作成

## 起動例

```
dev-reviewer: review_kind=code で実装差分をレビューし、CodeReviewResult を返してください。
```
