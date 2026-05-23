# product-manager SKILL

**独立スキル:** 開発チームにおける **子タスク 1 件**の進行管理（L3 ハブ）。

人間向け: [`README.md`](README.md) · workflow: [`workflows/development-delivery.yaml`](../../../workflows/development-delivery.yaml) v3 · I/O: [`docs/design/development-delivery-io.md`](../../../docs/design/development-delivery-io.md) · 委譲: [`docs/design/development-pm-assignment.md`](../../../docs/design/development-pm-assignment.md)

## 責務

1. `fetch_task.py --gid <task_gid>` で子 notes（背景・概要・完了条件・**profile**）を読む
2. 親エピック notes を文脈として参照（任意）
3. **delivery profile** を決定（省略時 `full`）:
   - `full` — 要件 → 設計 → 実装 → レビュー/QA → 事後仕様（非 UI）
   - **`full-ui`** — full + **UX 依存必須** + ux-reviewer 実装一致 review
   - `lite` — 設計 skip（**非 UI のみ**）
   - `doc-only` — 実装 skip
4. [`development-delivery.yaml`](../../../workflows/development-delivery.yaml) に沿い委譲:
   - **requirements-writer** — 要件 / 事後仕様（mode 指定）
   - **tech-designer** — 技術設計（full-ui は UX 仕様を引用）
   - **developer** — 実装・修正
   - **dev-reviewer** — 要件・設計・コード・mismatch レビュー
   - **ux-reviewer** — 実装 UI 一致（`full-ui` のみ）
   - **qa-verifier** — 動作検証
5. notes に `担当:` を追記してから委譲（[`development-pm-assignment.md`](../../../docs/design/development-pm-assignment.md)）
6. `MismatchReviewResult.fix_target == code` 時: developer へ修正依頼
7. 子の `done_when` を満たしたら **comment_task → complete_task -y → DeptWorkComplete**

## Asana 記録（必須・順序）

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py --gid <子GID> --agent product-manager --skill skills/development/product-manager/SKILL.md --summary "子タスク完了" --body "..." -y
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\complete_task.py --gid <子GID> -y
```

委譲先も各自 slug で `comment_task.py` を実行してから PM に報告する。

## やらないこと

- Handoff 新規作成（→ 企画チーム）
- Handoff JSON をチーム間入力として読む
- ディスパッチ（→ task-dispatcher）
- 新規 `skills/<organization>/<slug>/`（→ agent-creater）

## 成果物パス

| 種別 | パス |
|------|------|
| 要件 | `output/development/requirements/<task_gid>-requirements.md` |
| 設計 | `output/development/design/<task_gid>-design.md` |
| 事後仕様 | `output/development/specs/<task_gid>-spec.md` |
| レビュー | `output/development/reviews/` |

## 起動例

```
product-manager: 子タスク GID ○○ を profile=full-ui で development-delivery v3 に従い進めてください。UX 依存は notes ## 依存 を確認してください。
```
