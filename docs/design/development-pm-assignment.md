# product-manager 厳密運用 — チーム内アサインと delivery profile

| 版 | 1.0 |
| 日付 | 2026-05-23 |
| 適用 | 開発チーム L3（`development-delivery` v2） |

## 原則

1. **product-manager は自分で実装しない**（進行・委譲・完了集約を除く）。
2. PM が子タスク notes を読み、**delivery profile** と **担当 slug** を決める。
3. 委譲前に notes ヘッダに `担当:` を書く（[`update_task_notes.py`](../../skills/platform/asana-buddy/optional/update_task_notes.py)）。
4. **担当エージェントだけ**がそのフェーズを実行する。
5. 完了は **担当の comment_task → PM が次委譲 or 最終 complete**。

## notes ヘッダ（必須・先頭）

```markdown
チーム: development

profile: full
担当: requirements-writer
状態: assigned

```

| フィールド | 値 |
|------------|-----|
| `チーム` | `development` |
| `profile` | `full` \| `lite` \| `doc-only`（省略時 PM が `full` とみなす） |
| `担当` | [`agent-registry.yaml`](../../workflows/agent-registry.yaml) の slug |
| `状態` | `assigned` \| `in_progress` \| `review` \| `done` |

## delivery profile

| profile | スキップする段階 |
|---------|------------------|
| `full` | なし |
| `lite` | tech-designer / design review |
| `doc-only` | 設計・実装・code review・QA |

## 委譲先一覧（v2）

| 段階 | 担当 slug |
|------|-----------|
| 要件定義 | requirements-writer（mode=requirements） |
| 要件 review | dev-reviewer |
| 技術設計 | tech-designer |
| 設計 review | dev-reviewer |
| 実装 | developer |
| code review | dev-reviewer |
| 動作検証 | qa-verifier |
| 事後仕様 | requirements-writer（mode=as-built-spec） |
| mismatch | dev-reviewer |

## CLI

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\update_task_notes.py `
  --gid <GID> --department development --assignee tech-designer --status assigned --preserve-body -y

.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <GID> --show-assignee
```

## 参照

- [`development-delivery-io.md`](development-delivery-io.md)
- [`development-delivery.yaml`](../../workflows/development-delivery.yaml)
- [`skills/development/product-manager/SKILL.md`](../../skills/development/product-manager/SKILL.md)
