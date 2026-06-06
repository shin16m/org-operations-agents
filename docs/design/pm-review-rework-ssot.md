# PM レビュー差し戻し SSOT（修正タスク追加・完了再開禁止）

| 版 | 1.0 |
| 日付 | 2026-05-23 |
| 適用 | ux-pm / product-manager / analytics-pm · 各 reviewer / qa-verifier |

## 原則

| ルール | 内容 |
|--------|------|
| 提出先 | レビュー結果は **必ず PM へ**（`comment_task` + Result JSON） |
| OK | `status: passed` \| `passed_with_notes` → PM が review サブを complete → **次フェーズへ** |
| NG | `status: failed` → PM が **修正サブタスクを新規作成** → L3b でワーカー dispatch |
| **禁止** | 完了済み Asana タスクの **`complete_task.py --undo` による再開** |
| **禁止** | 完了済みサブの notes 書き換えだけで「やり直し」とみなすこと |
| **禁止** | **PM 委譲品質ゲート**（[`pm-assign-review-gate.md`](pm-assign-review-gate.md)）の承認サブを undo して再利用 |

`--undo` は dryrun  teardown 等の **運用ツール専用**。PM の差し戻しフローでは使わない。

## PM 委譲品質ゲート（assign 後・dispatch 前）

`pm_assign_subtasks` 直後の人間レビュー。差し戻し時は **新しい【レビュー】サブ**を追加し、旧承認サブは完了のまま残す（監査履歴）。詳細: [`pm-assign-review-gate.md`](pm-assign-review-gate.md)。

## フロー（L3 チーム内）

```
reviewer / qa-verifier
  → Result JSON を output/<dept>/reviews/ に保存
  → comment_task（PM へ報告）
       ↓
PM が Result を読む
  ├─ passed*  → review サブ complete → 次サブ（または親完了）
  └─ failed   → review サブ complete（レビュー作業自体は完了）
              → 修正サブタスクを親に追加
              → pm_emit_worker_prompt / WorkerDispatchSnippet
              → 修正完了後、再 review サブを **新規追加**（旧 review サブは触らない）
```

**ポイント:** failed でも **review サブは完了のまま**残す（監査履歴）。修正は **常に新サブ**。

## PM の NG 時必須アクション

1. Result JSON のパスと `findings` / `fix_target` を確認
2. 修正サブタスクを 1 件以上作成 — **推奨 CLI:** `python tools/pm_create_fix_subtask.py`（下記）または `pm_assign_subtasks` / Asana 手動
3. 修正サブ notes に最低限含める:
   - `担当: <worker slug>`
   - `## 修正依頼` — 元 review JSON パス、指摘要約、`fix_target`（あれば）
   - `done_when` — 修正後の成果物パス（上書き or 版付き）
4. L3b: `python tools/pm_emit_worker_prompt.py --parent <親GID> --department <dept>`  
   または fix 作成時: `python tools/pm_create_fix_subtask.py ... --emit-dispatch -y`
5. 修正サブ complete 後、**再 review サブ**を新規追加（タイトル例: `[re-review] dev-reviewer — code (R2)`）
6. 旧成果物を上書きする前に `output/<dept>/_archive/` へ退避（任意だが推奨）

### 修正サブタスク命名（推奨）

| 種別 | タイトル例 |
|------|------------|
| 修正 | `[fix] developer — code review findings (R1)` |
| 再 review | `[re-review] dev-reviewer — code (R2)` |

`R{n}` は同一ゲートの修正ラウンド。Asana 上で履歴が追えるようにする。

## 分析 ↔ 画面接続検証の差し戻し（full-ui + insights）

dev-reviewer（接続検証 / mismatch）または qa-verifier が **bundle と画面の不一致**を検出した場合:

| finding 種別 | fix_target | 修正担当 |
|--------------|------------|----------|
| `top_factors` / `insights` / `signatures` 不一致 | `code` | developer |
| 鮮度未表示 | `code` | developer |
| bundle フィールドの定数コピー残存 | `code` | developer |
| 要件に bundle consume 記載なし | `document` | requirements-writer |
| bundle パス誤り（`## 依存`） | — | product-manager が analytics-pm へエスカレーション |

修正サブ notes の `## 修正依頼` に **bundle パス**と **不一致フィールド名**を必ず含める。再 review は接続検証サブを新規追加（`[re-review] dev-reviewer — analysis connection (R{n})`）。

参照: [`development-delivery-io.md`](development-delivery-io.md) · [`insights-dashboard-consume-io.md`](insights-dashboard-consume-io.md)

## CLI — 修正サブ作成

```powershell
# [fix] のみ（デフォルト）。review JSON パスは output/<dept>/reviews/ 推奨
python tools/pm_create_fix_subtask.py `
  --parent <PM子GID> `
  --review-json output/development/reviews/<gid>-code-review.json `
  -y

# [fix] + [re-review] を同時作成（省略可 — 修正完了後に --rereview-only 推奨）
python tools/pm_create_fix_subtask.py --parent <GID> --review-json <path> --with-rereview -y

# 修正完了後、再 review サブのみ
python tools/pm_create_fix_subtask.py --parent <GID> --review-json <path> --rereview-only --round 2 -y

# 計画確認（Asana 書き込みなし）
python tools/pm_create_fix_subtask.py --parent <GID> --review-json <path> --dry-run

# 修正サブ作成 + WorkerDispatchSnippet 出力
python tools/pm_create_fix_subtask.py --parent <GID> --review-json <path> --emit-dispatch -y
```

| オプション | 説明 |
|------------|------|
| `--department` | `output/` / `skills/` 以外のパス時は必須 |
| `--round N` | 省略時は既存 `[fix]` サブから R{n} を自動採番 |
| `--fix-assignee` | 分析 `production_deploy_gate` 等で PM が worker を指定 |
| `--dry-run` | 作成予定の name / assignee のみ JSON 出力 |

**前提:** review JSON の `status` は `failed`（`[fix]` 作成時）。`passed*` では CLI はエラー。

**例:** [`skills/development/examples/review-result.code-failed.example.json`](../../skills/development/examples/review-result.code-failed.example.json) · 生成物参考 [`assign-plan.fix-code.example.json`](../../skills/development/examples/assign-plan.fix-code.example.json)

## fix_target 別の修正担当

| Result | fix_target | 修正サブの `担当:` |
|--------|------------|-------------------|
| DocReviewResult | （message 参照） | requirements-writer / tech-designer 等 |
| CodeReviewResult | — | developer |
| VerificationResult | — | developer |
| MismatchReviewResult | `document` | requirements-writer（as-built-spec） |
| MismatchReviewResult | `code` | developer |
| UxReviewResult | `ux_spec` | ux-designer |
| UxReviewResult | `implementation` | developer |
| AnalysisDocReviewResult / DeployGateResult | — | analytics-pm が findings から worker を決定 |

ゲート表: 各 `*-delivery-io.md` の「必須ゲート」。

## 企画チーム（例外）

`plan-reviewer` の `needs_revision` は Asana サブではなく **Handoff JSON の改訂**:

- orchestrator → **issue-story-planner** 再実行 → **plan-reviewer** 再実行
- Asana 投入前のため `--undo` / 修正サブは通常発生しない

契約: [`plan-reviewer-contract.md`](plan-reviewer-contract.md)

## 関連

- L3b dispatch: [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md)
- レビュー Result 一覧: [`dept-work-io.md`](dept-work-io.md#チーム内レビュー結果)
- PM アサイン: `*-pm-assignment.md`
