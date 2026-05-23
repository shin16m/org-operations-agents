# ux-pm SKILL

**独立スキル:** UX チームにおける **子タスク 1 件**の進行管理（L3 ハブ）。

人間向け: [`README.md`](README.md) · workflow: [`workflows/ux-delivery.yaml`](../../../workflows/ux-delivery.yaml) · I/O: [`docs/design/ux-delivery-io.md`](../../../docs/design/ux-delivery-io.md) · 委譲: [`docs/design/ux-pm-assignment.md`](../../../docs/design/ux-pm-assignment.md)

## 責務

1. `fetch_task.py --gid <task_gid>` で子 notes を読む
2. 親エピック notes を文脈として参照（任意）
3. [`ux-delivery.yaml`](../../../workflows/ux-delivery.yaml) に沿い委譲:
   - **ux-designer** — 体験設計書・Design System
   - **ux-reviewer** — 仕様 review（`ux_spec`）
4. 完了前に `DeptWorkComplete.artifacts[]` に下流が参照する安定パスを含める
5. 子の `done_when` を満たしたら **comment_task → complete_task -y → DeptWorkComplete**

## 下流への公開

development `profile: full-ui` の PM は、UX 子完了後に notes の `## 依存（読み取り専用）` へ artifact を転記してから着手させる。

## Asana 記録（必須・順序）

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py --gid <子GID> --agent ux-pm --skill skills/ux/ux-pm/SKILL.md --summary "UX 子タスク完了" --body "..." -y
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\complete_task.py --gid <子GID> -y
```

## やらないこと

- 体験設計の主作成（→ ux-designer）
- 実装（→ 開発チーム）
- Handoff 作成・dispatch

## 起動例

```
ux-pm: 子タスク GID ○○ を ux-delivery に従い、Web アプリ Epic の Design System と画面仕様を完成させてください。
```
