# PM → ワーカー dispatch SSOT（L3 チーム内第 2 配賦）

| 版 | 1.0 |
| 日付 | 2026-05-23 |
| 適用 | ux-pm / product-manager / analytics-pm（planning-pm は別フロー） |

## 問題（v1 dryrun / 実運用で起きていたこと）

| 層 | 誰が動く | 実態 |
|----|----------|------|
| L2 task-dispatcher | **PM のみ** | 正常（設計どおり） |
| L3 PM intake | PM がサブタスク作成 | 正常 |
| L3 worker | **動いていない** | PM が worker 役まで代行 · dryrun 脚本が comment だけ代投 |

**L2 で PM しか dispatch されないのは正しい。**  
不足していたのは **L3 で PM がワーカーを別セッション起動する契約**。

## 二段 dispatch モデル

```
L2  task-dispatcher     →  PM（子タスク 1 件）
L3a PM intake            →  pm_assign_subtasks（サブ作成）
L3b PM worker-dispatch   →  サブ 1 件 → ワーカー 1 セッション（必須・繰り返し）
L3c PM complete          →  サブ complete 集約 → 親 DeptWorkComplete
```

**PM の 1 セッションでやること:** L3a + **現在アクティブなサブ 1 件の L3b 起動文出力** + サブ完了確認。  
**PM の 1 セッションでやらないこと:** 複数サブの成果物を連続で自分で書く。

## PM の必須フロー（サブタスク作成後）

```
1. fetch_task.py --gid <親> --list-subtasks
2. 未完了サブのうち workflow 順で先頭 1 件を選ぶ
3. fetch_task.py --gid <サブ> --show-assignee で 担当: <worker> を確認
4. 下記 WorkerDispatchSnippet を利用者 / 別エージェントセッションへ渡す
5. PM セッションはここで一旦終了（ワーカー完了を待つ）
6. ワーカー comment_task 後、PM が当該サブを complete → 4 に戻る
7. 全サブ完了後、親 comment → complete → DeptWorkComplete
```

**禁止:** ワーカー起動文を出さず、PM がサブの done_when まで自分で実行する。

## WorkerDispatchSnippet（テンプレ）

PM は **サブ 1 件ごと**に次を出力する（[`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md#共通--ワーカー向け-snippetpm-がサブ委譲時に添付) と同一）。

```
【WorkerDispatch】department={department} parent={parent_gid} sub={sub_gid} worker={worker_slug}

あなたは {worker_slug} スキルです。Asana サブタスク GID {sub_gid} のみを実行してください。

1. fetch_task.py --gid {sub_gid} --show-assignee で 担当: {worker_slug} を確認（不一致なら PM へ）
2. サブ notes の done_when に従い成果物を作成
3. comment_task.py --agent {worker_slug} --skill {skill_path_from_registry} -y
4. PM へ完了報告（PM が complete_task.py --gid {sub_gid} -y）

親タスク {parent_gid} の workflow 全体・他サブタスクは実行しないこと。
```

## CLI — ワーカー起動文の生成

```powershell
# 親子の未完了サブから workflow 順先頭の WorkerDispatchSnippet を表示
python tools/pm_emit_worker_prompt.py --parent <親GID> --department development

# 全未完了サブ分を一覧
python tools/pm_emit_worker_prompt.py --parent <親GID> --department ux --all
```

## チーム別 assignment SSOT

| department | PM | worker 例 |
|------------|-----|-----------|
| ux | ux-pm | ux-designer, ux-reviewer |
| development | product-manager | requirements-writer, developer, **ux-reviewer**（UX 所属・registry 参照）, … |
| analysis | analytics-pm | data-architect, data-engineer, … |

## dryrun との関係

| 種別 | ワーカー |
|------|----------|
| `run_all_teams_dryrun.py` v1 | **Asana comment のみ代投**（別エージェントセッションなし）→ wiring 検証用 |
| 本番 / v2 dryrun | PM が `pm_emit_worker_prompt.py` → **別セッションで worker SKILL 起動** |

## レビュー NG 時（L3b の続き）

review サブで `failed` → PM は **`pm_create_fix_subtask.py`** で [fix] サブ作成 → L3b dispatch。完了済みサブの `--undo` は禁止。

```powershell
python tools/pm_create_fix_subtask.py --parent <親GID> --review-json output/<dept>/reviews/<file>.json -y
```

詳細: [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)

## 関連

- L2 起動: [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md)
- レビュー差し戻し: [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)
- チーム内アサイン: `*-pm-assignment.md`
- L2/L3 全体: [`department-model.md`](department-model.md)
