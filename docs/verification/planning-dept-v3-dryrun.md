# default v3 ドライラン記録 — 企画チーム L3 化 + 開発チーム dispatch

実施日: 2026-05-23

## 課題（intake）

default v3 workflow（`intake → bootstrap → dispatch → planning-delivery`）が E2E 手順どおり再現できるか検証する。

## 成果物パス

| 段階 | ファイル |
|------|----------|
| bootstrap Handoff | `docs/verification/fixtures/planning/handoff/bootstrap.planning-dept-v3-dryrun.json` |
| 本番 Handoff | `docs/verification/fixtures/planning/handoff/handoff.planning-dept-v3-dryrun.json` |
| PlanReviewResult | `docs/verification/fixtures/planning/plan-review/plan-review.planning-dept-v3-dryrun.json` |
| 組織モデル | `docs/design/department-model.md` |
| 本記録 | `docs/verification/planning-dept-v3-dryrun.md` |

## Asana

| 項目 | GID / URL |
|------|-----------|
| 親エピック | `1215080861877116` |
| 親 URL | https://app.asana.com/1/1214766054680431/project/1215080644653452/task/1215080861877116 |
| 企画子（bootstrap） | `1215080914464156` — **completed** |
| 開発子【2/2】 | `1215080863094890` — dispatch 検証用 |

---

## 段階別結果 — L1/L3 企画チーム

| # | step | 担当 | 結果 |
|---|------|------|------|
| 0 | intake | workflow-orchestrator | bootstrap Handoff 生成 |
| 1 | bootstrap | asana-buddy | 親 + 企画子作成（`チーム: planning`） |
| 2 | dispatch | task-dispatcher | `department=planning` → planning-pm |
| 3a | handoff_plan | issue-story-planner | 本番 Handoff 保存 |
| 3b | plan_review | plan-reviewer | `passed_with_notes` |
| 3c | pm_gate | planning-pm | 承認 → asana_execute |
| 3d | asana_execute | asana-buddy | `--if-not-exists` で skip（親既存） |
| 3e | pm_complete | planning-pm | comment → complete |

---

## 段階別結果 — L2/L3 開発チーム

| # | step | 担当 | 結果 |
|---|------|------|------|
| 4 | 子追加 | asana-buddy（手動） | 親 GID 指定で【2/2】作成（`チーム: development`） |
| 5 | dispatch | task-dispatcher | `DispatchRequest` → product-manager |
| 6 | 作業 | product-manager | 本記録更新 + `department-model.md` 整理反映 |
| 7 | pm_complete | product-manager | comment → complete → `DeptWorkComplete` |

### dispatch 用 prompt_snippet（開発チーム）

```
DispatchRequest: task_gid=1215080863094890, parent_gid=1215080861877116, department=development
organizations.yaml に従い product-manager 用 prompt_snippet を返してください。
```

**チーム間入力:** 子 notes のみ（Handoff JSON は読まない — [`department-model.md`](../design/department-model.md)）

---

## 所見

1. **bootstrap → 企画 dispatch** — 有効。
2. **本番 Handoff + 既存親** — **2026-05-23 改善:** `--if-not-exists` は sync モード（親 notes 更新・不足子 create・bootstrap 企画子 fuzzy マッチ）。当時は手動 `create_subtask` で対応。
3. **開発チーム dispatch** — `チーム: development` notes から product-manager 起動可能。チーム間 I/O は notes のみで足りる。
4. **bootstrap 企画子 fuzzy マッチ** — `チーム: planning` のみの子を Handoff 先頭 planning 子に対応付け（1 件のみ）。

---

## チーム表記 dry-run（2026-05-23）

「課」→「チーム」改称後、`チーム:` 出力と legacy `課:` 読取の検証。

### コマンド

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\handoff_to_asana.py `
  --handoff .\output\planning\handoff\handoff.planning-dept-v3-dryrun.json `
  --require-review-result .\output\planning\plan-review\plan-review.planning-dept-v3-dryrun.json `
  --parent 1215080861877116 --if-not-exists --dry-run -y
```

### 結果

| 項目 | 結果 |
|------|------|
| PlanReviewResult | `passed_with_notes` |
| sync dry-run | `parent=1215080861877116 update_parent=True subtasks=2` |
| 新規 notes 生成（ローカル） | `チーム: planning` / `チーム: development` |
| 既存 Asana 子 notes | legacy `課: planning` / `課: development`（投入当時） |
| `parse_task_assignment` | legacy `課:` から `planning` / `development` を正しく解決 |

### 所見

- **書込**は `チーム:`、**読取**は `課:` / `チーム:` 両対応 — dispatch 互換 OK。
- 既存エピックの notes を `チーム:` に揃えるには、上記コマンドから `--dry-run` を外して sync 実行（`-y` 付き）。

### sync 本番実行（2026-05-23）

```powershell
# --dry-run なしで実行済み
handoff_to_asana.py ... --parent 1215080861877116 --if-not-exists -y
```

| 項目 | 結果 |
|------|------|
| 親 notes | 更新 |
| 企画子 `1215080914464156` | fuzzy マッチ → タイトル【1/2・企画】・notes `チーム: planning` |
| 開発子 `1215080863094890` | updated → notes `チーム: development` |

---

## 完了状態

- [x] 企画子 complete
- [x] 開発子【2/2】complete（product-manager）
- [x] 親エピック complete（orchestrator 推奨）

## 関連

- [`department-model.md`](../design/department-model.md)
- [`planning-dept-v3-smoke.md`](planning-dept-v3-smoke.md)
- E2E: [`default-workflow.md`](../e2e/default-workflow.md)
