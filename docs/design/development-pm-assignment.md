# product-manager 厳密運用 — チーム内アサインと delivery profile

| 版 | 1.1 |
| 日付 | 2026-05-23 |
| 適用 | 開発チーム L3（`development-delivery` v3） |

## 原則

1. **product-manager は自分で実装しない**（進行・委譲・完了集約を除く）。
2. PM が子タスク notes を読み、**delivery profile** と **担当 slug** を決める。
3. 委譲前に notes ヘッダに `担当:` を書く（[`update_task_notes.py`](../../skills/platform/asana-buddy/optional/update_task_notes.py)）。
4. **担当エージェントだけ**がそのフェーズを実行する。
5. 完了は **担当の comment_task → PM が次委譲 or 最終 complete**。

## notes ヘッダ（必須・先頭）

```markdown
チーム: development

profile: full-ui
担当: requirements-writer
状態: assigned

```

| フィールド | 値 |
|------------|-----|
| `チーム` | `development` |
| `profile` | `full` \| **`full-ui`** \| `lite` \| `doc-only`（省略時 PM が `full` とみなす） |
| `担当` | [`agent-registry.yaml`](../../workflows/agent-registry.yaml) の slug |
| `状態` | `assigned` \| `in_progress` \| `review` \| `done` |

## delivery profile

| profile | スキップする段階 | 備考 |
|---------|------------------|------|
| `full` | なし（ux_implementation 除く） | API / 非 UI |
| **`full-ui`** | なし | **`## 依存` に UX artifact 必須** |
| `lite` | tech-designer / design review | **画面タッチの子では禁止** |
| `doc-only` | 設計・実装・code/ux/verification review | 仕様のみ |

### full-ui 着手チェック

- [ ] 同一 Epic の UX 子が Asana 上 **completed**
- [ ] notes に `## 依存（読み取り専用）` で UX 仕様パスがある
- [ ] `profile: full-ui` をヘッダに明記

未充足 → UX チームまたは企画 PM へ差し戻し。**developer へ委譲しない。**

## 委譲先一覧（v3）

| 段階 | 担当 slug |
|------|-----------|
| 要件定義 | requirements-writer（mode=requirements） |
| 要件 review | dev-reviewer |
| 技術設計 | tech-designer |
| 設計 review | dev-reviewer |
| 実装 | developer |
| code review | dev-reviewer |
| UX 実装一致 review | **ux-reviewer**（`full-ui` のみ） |
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
- [`ux-delivery-io.md`](ux-delivery-io.md)
- [`development-delivery.yaml`](../../workflows/development-delivery.yaml)
- [`skills/development/product-manager/SKILL.md`](../../skills/development/product-manager/SKILL.md)
