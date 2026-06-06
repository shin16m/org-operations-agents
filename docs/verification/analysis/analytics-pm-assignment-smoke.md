# Smoke — analytics-pm 厳密アサイン（v2）

| 前提 | `.env` に `ASANA_TOKEN`, `ASANA_PROJECT_ID` |
| 対象 | analysis 子タスク GID（Epic 内・`department=analysis`） |
| 適用 | `analysis-delivery` v2 · PM は進行のみ（要件/リリースは **analytics-requirements-writer**） |

## 1. 親タスクの profile / 担当

```powershell
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\update_task_notes.py `
  --gid <PARENT_GID> --department analysis --assignee analytics-pm --status in_progress --preserve-body -y
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <PARENT_GID> --show-assignee
```

期待: `チーム: analysis` · `担当: analytics-pm` · notes に `profile:` が存在

## 2. チーム内サブタスク作成（catalog profile 例）

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent <PARENT_GID> --plan .\skills\analysis\examples\assign-plan.catalog-v2.json `
  --department analysis --update-parent-assignee analytics-pm -y
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <PARENT_GID> --list-subtasks
```

期待:

- 【1】`担当: analytics-requirements-writer`（要件）
- 【2】`担当: analysis-reviewer`
- 【3】`担当: data-architect`
- 【5】`担当: data-steward`
- 【7】`担当: analytics-requirements-writer`（リリース · `mode=release`）

PM が要件/リリースサブを自分に割り当てていないこと。

## 3. ワーカー着手前確認

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <SUB_GID> --show-assignee
```

期待: 起動するエージェント slug と `担当:` が一致。

## 4. レビュー NG（修正タスク）

PM 差し戻しは **修正サブタスクの新規追加**。`--undo` は使わない。

参照: [`pm-review-rework-ssot.md`](../design/pm-review-rework-ssot.md)

## 5. 自動 dryrun

```powershell
$env:PYTHONIOENCODING='utf-8'
# full profile（10 サブ）
.\tools\run_analysis_v2_dryrun.py
# profile 別（catalog 7 / insights 11 / model-serve 14 サブ）
.\tools\run_analysis_profile_dryrun.py --profile catalog
.\tools\run_analysis_profile_dryrun.py --profile all
```

記録: [`analysis-delivery-v2-dryrun.md`](analysis-delivery-v2-dryrun.md) · [`analysis-profile-dryrun.md`](analysis-profile-dryrun.md) · 分析→dev 継ぎ目: [`analysis-to-dev-dryrun.md`](../cross-team/analysis-to-dev-dryrun.md) · 全チーム: [`all-teams-dryrun.md`](../cross-team/all-teams-dryrun.md)

## 参照

- [`analytics-pm-assignment.md`](../design/analytics-pm-assignment.md)
- [`assign-plan.catalog-v2.json`](../../skills/analysis/examples/assign-plan.catalog-v2.json)
- [`assign-plan.dryrun-v2.json`](../../skills/analysis/examples/assign-plan.dryrun-v2.json)（full profile · 10 サブ）
