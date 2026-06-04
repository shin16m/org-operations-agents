# requirements-writer SKILL

**独立スキル:** product-manager から **サブタスク**として委譲された **文書作成**（要件定義・事後詳細仕様）。

PM 委譲: [`docs/design/development-pm-assignment.md`](../../../docs/design/development-pm-assignment.md)

## 着手前（必須）

1. `fetch_task.py --gid <task_gid> --show-assignee` で **担当が requirements-writer** であることを確認する。
2. 一致しない場合は作業せず product-manager へエスカレーション。

## モード

| mode | 成果物 | タイミング | 次 |
|------|--------|------------|-----|
| `requirements` | 要件定義書 | workflow 序盤 | dev-reviewer（`review_kind: requirements`） |
| `as-built-spec` | 事後詳細仕様書 | 実装・検証後 | dev-reviewer（`review_kind: mismatch`） |

PM の依頼または workflow 段階で mode を確定する。

## 責務

### mode=requirements

- 子タスク notes と親エピック notes から要件定義書を作成
- パス: `output/development/requirements/<task_gid>-requirements.md`
- 完了後 **dev-reviewer** へレビュー依頼

### mode=as-built-spec

- 実装済み成果を反映した詳細仕様書を作成
- パス: `output/development/specs/<task_gid>-spec.md`
- 完了後 **dev-reviewer**（mismatch）へ依頼

## Asana 記録

完了前に `comment_task.py`（`--agent requirements-writer`）。[`agent-asana-comment-signature.md`](../../../docs/design/agent-asana-comment-signature.md) §4–5 — **実施内容 · 成果物パス · 次の状態**（です・ます調）。`--action` 繰り返し可。

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py --gid <子GID> --agent requirements-writer --skill skills/development/requirements-writer/SKILL.md --summary "..." -y
```

## やらないこと

- 技術設計書（→ tech-designer）
- コード実装（→ developer）
- レビュー本体（→ dev-reviewer / qa-verifier）
- PM 進行（→ product-manager）

## 起動例

```
requirements-writer: 子タスク GID 1215081161914216 を mode=requirements で要件定義書を作成し、dev-reviewer へレビュー依頼してください。
```
