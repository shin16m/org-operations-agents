# ux-pm 厳密運用 — チーム内アサイン

| 版 | 1.0 |
| 日付 | 2026-05-23 |
| 適用 | UX チーム L3（`ux-delivery` v1） |

## 原則

1. **ux-pm は自分で体験設計しない**（進行・artifact 公開・完了集約を除く）。
2. PM が子 notes を読み、**担当 slug** を決める。
3. 委譲前に notes ヘッダに `担当:` を書く。
4. **担当エージェントだけ**がそのフェーズを実行する。
5. 完了は **担当の comment_task → PM が complete**。

## notes ヘッダ（必須・先頭）

```markdown
チーム: ux

担当: ux-designer
状態: assigned

```

| フィールド | 値 |
|------------|-----|
| `チーム` | `ux` |
| `担当` | `ux-designer` \| `ux-reviewer` |
| `状態` | `assigned` \| `in_progress` \| `review` \| `done` |

## 委譲先一覧

| 段階 | 担当 slug |
|------|-----------|
| 体験設計 | ux-designer |
| 仕様 review | ux-reviewer（`review_kind: ux_spec`） |
| 実装一致 review | ux-reviewer（`review_kind: ux_implementation`）— development PM から依頼 |

## CLI

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\update_task_notes.py `
  --gid <GID> --department ux --assignee ux-designer --status assigned --preserve-body -y
```

## 参照

- [`ux-delivery-io.md`](ux-delivery-io.md)
- [`workflows/ux-delivery.yaml`](../../workflows/ux-delivery.yaml)
