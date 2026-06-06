# Asana コメント詳細化 — delivery 記録（事後補完）

| 項目 | 内容 |
|------|------|
| 実施 | 2026-05-23 |
| 方針 | **B（監査証跡の事後補完）** — **レガシー例外**。2026-06-06 以降の通常 epic では [`pm-worker-separation-enforcement.md`](../design/pm-worker-separation-enforcement.md) により一括 stamp は CLI で拒否される |
| 親エピック GID | `1215083271430850` |
| 開発子 GID | `1215083271788346` |
| 本体 commit | `78829c2` |

## 背景

企画 gate 承認後、同一セッションで **product-manager が開発子の doc 更新を代行**し、doc-only フロー（`pm_assign_subtasks` → ワーカー dispatch）を省略した。

## 本体（先行完了）

| ファイル | 内容 |
|----------|------|
| `docs/design/agent-asana-comment-signature.md` | v1.1 依頼者向けガイド |
| `docs/design/dispatch-prompt-ssot.md` | コメント要件横展開 |
| `docs/design/dept-work-io.md` | §4–5 参照 |
| `skills/platform/asana-buddy/SKILL.md` | 本文記載ルール |
| `tools/run_all_teams_dryrun.py` | `agent_comment_body()` |

## 事後補完（本記録）

### output/development（ローカル · gitignore）

| 種別 | パス |
|------|------|
| assign plan | `output/development/assign-plans/asana-comment-detail.doc-only.json` |
| 要件 | `output/development/requirements/1215083271788346-requirements.md` |
| 事後仕様 | `output/development/specs/1215083271788346-spec.md` |
| 要件 review | `output/development/reviews/1215083271788346-requirements.review.json` |
| mismatch review | `output/development/reviews/1215083271788346-mismatch.review.json` |

### Asana 監査サブ（開発子下）

| # | GID | 担当 | 状態 |
|---|-----|------|------|
| 1 | `1215083572045782` | requirements-writer | complete |
| 2 | `1215083606709418` | dev-reviewer | complete |
| 3 | `1215083572081598` | requirements-writer | complete |
| 4 | `1215083592014780` | dev-reviewer | complete |

### エピック

- 親 `1215083271430850` — **complete**（workflow-orchestrator 署名コメント後）

## 再現コマンド（監査サブ作成）

```powershell
$env:PYTHONIOENCODING='utf-8'

# 1. assign plan（事前に output/development 成果物を作成）
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent 1215083271788346 `
  --plan output/development/assign-plans/asana-comment-detail.doc-only.json `
  --department development --update-parent-assignee product-manager -y

# 2. 各サブ: comment_task.py（担当 slug）→ complete_task.py -y
# 3. 親エピック complete
```

## 教訓

1. **gate 承認 ≠ development 実装開始**。`asana_execute` 後は **task-dispatcher → product-manager intake** が必須。
2. `docs/design/` 更新のみでも **profile: doc-only** + ワーカー委譲が正規ルート。
3. PM 代行で本体を先に終えた場合は、本記録の **方針 B** で Asana / output を後追い補完する。

## 関連

- Handoff: `output/planning/handoff/handoff.asana-comment-detail.json`
- assign plan 例: [`assign-plan.org-meta-doc-v1.json`](../../skills/development/examples/assign-plan.org-meta-doc-v1.json)
