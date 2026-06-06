# UX チーム + development full-ui — dry-run 手順

| 項目 | 内容 |
|------|------|
| 目的 | UX 第4チーム dispatch・**PM サブタスクアサイン**・development `full-ui` の通し確認 |
| workflow | `ux-delivery` v1 · `development-delivery` v3 |
| 前提 | default v3 企画完了済み Epic |

## 1. Handoff に UX 子を含める

execution 系 subtask 例:

```json
{
  "title": "【2/4・UX】Web アプリ体験設計",
  "background": "…",
  "summary": "Design System と主要画面仕様",
  "done_when": "ux_review_passed・artifacts 公開",
  "department": "ux"
}
```

参照: [`handoff-v12-department.md`](../design/handoff-v12-department.md)

## 2. UX 子 — dispatch

```
子タスク GID <UX_CHILD> を ux に配賦し、ux-delivery を起動してください。
```

期待: entry `ux-pm` · workflow `ux-delivery`

## 3. ux-pm — サブタスク分解（必須）

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent <UX_CHILD_GID> `
  --plan .\skills\ux\examples\assign-plan.web-app-v1.json `
  --department ux --update-parent-assignee ux-pm -y
```

期待:

- 親 notes → `担当: ux-pm` · `状態: in_progress`
- 子サブ 3 件（ux-designer ×2 · ux-reviewer ×1）各 `チーム: ux` + `担当:`

各ワーカーは `fetch_task.py --gid <サブGID> --show-assignee` で担当確認後に着手。

## 4. UX 完了 — artifact

| 成果物 | パス例 |
|--------|--------|
| 体験設計書 | `output/ux/specs/<gid>-ux-spec.md` |
| Design System | `output/ux/design-system/<gid>-design-system.md` |
| レビュー | `output/ux/reviews/<gid>-ux-spec-review.json` |

全サブ完了後、ux-pm が `DeptWorkComplete.artifacts[]` に安定パスを含めて親を complete。

## 5. development 子 — 依存転記

product-manager が notes に追記:

```markdown
profile: full-ui

## 依存（読み取り専用）

| 種別 | 参照 | バージョン | 提供チーム |
|------|------|------------|------------|
| UX 仕様 | output/ux/specs/<ux_gid>-ux-spec.md | v1.0 | ux |
| Design System | output/ux/design-system/<ux_gid>-design-system.md | v1.0 | ux |
```

## 6. development full-ui — 追加ゲート

code review 後、product-manager が ux-reviewer へ `ux_implementation` 委譲。

## 7. チェックリスト

- [ ] ux-pm が **サブタスク未作成のまま** ux-designer へ親丸ごと委譲していない
- [ ] 各サブ notes に `担当:` がある
- [ ] ワーカーが `--show-assignee` で担当確認している
- [ ] UX 親完了前に development full-ui が着手していない
- [ ] `## 依存` なし full-ui で development PM が差し戻す

## 関連

- [`ux-pm-assignment.md`](../design/ux-pm-assignment.md)
- [`analytics-pm-assignment.md`](../design/analytics-pm-assignment.md)（同等運用）
- [`ux-delivery-io.md`](../design/ux-delivery-io.md)
