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

### design レビュー追加

- **実行契約** 4 項目（起動 / 依存パス / エラー UI / mock vs 本番）のいずれか欠落 → **failed**（`category: design_execution_contract`）

### code レビュー追加

- `output/development/smoke/<gid>.md` が無い、または Must AC 未実行 → **failed**（`category: developer_smoke`）

## Asana 添付の確認（requirements / mismatch）

`review_kind` が `requirements` または `mismatch` のとき、レビュー開始前に対象 md が **当該 dev-reviewer review サブ**（assign plan 上の review サブタスク）に attach 済みであることを確認する。

```powershell
# 本サブ（review サブ）で確認 — 原則こちらを正とする
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\attach_task_files.py --gid <review_sub_gid> --list
```

- `requirements`: `*-requirements.md` が **review サブ**一覧に無ければ **failed**（attach 欠落）
- `requirements`: **§受け入れ基準** の Must AC に検証コマンド列が無い → **failed**（`category: acceptance_criteria`）。参照: [`acceptance-criteria-template.md`](../../../docs/design/acceptance-criteria-template.md)
- `mismatch`: `*-spec.md` が **review サブ**一覧に無ければ **failed**
- attach 欠落時は PM へ差し戻し（requirements-writer の review サブ伝播手順の欠落修正）。レビュー JSON は `status: failed` + finding に `category: io_contract`

## MismatchReviewResult

- `fix_target: document` → PM が **requirements-writer 向け修正サブ**を新規作成
- `fix_target: code` → PM が **developer 向け修正サブ**を新規作成

### full-ui + 分析連携時の追加観点（`review_kind: mismatch` または接続検証サブ）

notes `## 依存` に DashboardBundle がある場合、以下を **3 件以上**確認する（[`development-delivery-io.md`](../../../docs/design/development-delivery-io.md) チェックリスト）:

| # | 観点 | failed 条件の例 |
|---|------|----------------|
| 1 | **top_factors 一致** | 画面上位因子の名称が `top_factors[].name` と不一致 |
| 2 | **insights 一致** | `insights.known` / `unknown` の件数または文言が画面と乖離 |
| 3 | **定数残存なし** | `app.js` 等に bundle フィールド（`top_factors` / `signatures` 等）のハードコードが残存 |
| 4 | **鮮度メタ** | `meta.generated_at` が UI に未表示 |

`fix_target: code` を基本とする。要件書自体の不足は `document`。

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
