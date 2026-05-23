# UX チーム + development full-ui — dry-run 手順

| 項目 | 内容 |
|------|------|
| 目的 | UX 第4チーム dispatch と development `profile: full-ui` の通し確認 |
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

```json
{
  "title": "【3/4・開発】ダッシュボード UI 実装",
  "department": "development",
  "summary": "UX 仕様に基づきフロント実装",
  "done_when": "ux_implementation + verification passed"
}
```

参照: [`handoff-v12-department.md`](../design/handoff-v12-department.md)

## 2. UX 子 — dispatch

```
子タスク GID <UX_CHILD> を ux に配賦し、ux-delivery を起動してください。
```

期待: entry `ux-pm` · workflow `ux-delivery`

## 3. UX 完了 — artifact

| 成果物 | パス例 |
|--------|--------|
| 体験設計書 | `output/ux/specs/<gid>-ux-spec.md` |
| Design System | `output/ux/design-system/<gid>-design-system.md` |
| レビュー | `output/ux/reviews/<gid>-ux-spec-review.json` |

`DeptWorkComplete.artifacts[]` に上記パスを含める。

## 4. development 子 — 依存転記

product-manager が notes に追記:

```markdown
profile: full-ui

## 依存（読み取り専用）

| 種別 | 参照 | バージョン | 提供チーム |
|------|------|------------|------------|
| UX 仕様 | output/ux/specs/<ux_gid>-ux-spec.md | v1.0 | ux |
| Design System | output/ux/design-system/<ux_gid>-design-system.md | v1.0 | ux |
```

## 5. development full-ui — 追加ゲート

code review 後:

```
ux-reviewer: 実装 UI を ux_implementation でレビューしてください。
```

`UxReviewResult` → `ux_implementation_review_passed` → qa-verifier

## 6. チェックリスト

- [ ] `organizations.yaml` に `ux` 行がある
- [ ] `DispatchRequest.department=ux` が受理される
- [ ] UX 子完了前に development full-ui が着手していない
- [ ] `## 依存` なし full-ui で PM が差し戻す
- [ ] ux-reviewer が development から委譲可能

## 関連

- [`ux-delivery-io.md`](../design/ux-delivery-io.md)
- [`development-delivery-io.md`](../design/development-delivery-io.md)
- [`team-conventions.md`](../design/team-conventions.md)
