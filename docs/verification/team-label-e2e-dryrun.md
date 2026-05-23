# チーム表記 E2E — Asana 実行記録

実施日: 2026-05-23

## 課題（intake）

default v3 + `チーム:` notes で **新規 Asana エピック**を作成し、企画チーム → 開発チームまで実行する。

## 成果物

| 段階 | ファイル |
|------|----------|
| bootstrap | `output/planning/handoff/bootstrap.team-label-e2e.json` |
| Handoff | `output/planning/handoff/handoff.team-label-e2e.json` |
| PlanReview | `output/planning/plan-review/plan-review.team-label-e2e.json` |
| 本記録 | `docs/verification/team-label-e2e-dryrun.md` |

## Asana

| 項目 | GID / URL |
|------|-----------|
| 親エピック | `1215081162064645` |
| 親 URL | https://app.asana.com/1/1214766054680431/project/1215080644653452/task/1215081162064645 |
| 企画子【1/2】 | `1215081115164244` — **completed** |
| 開発子【2/2】 | `1215081161914216` — **completed** |

---

## 段階別結果 — L1 bootstrap

| # | step | 担当 | 結果 |
|---|------|------|------|
| 1 | bootstrap | asana-buddy | `created_parent 1215081162064645` · 企画子 `1215081115164244`（`チーム: planning`） |

```powershell
handoff_to_asana.py --handoff bootstrap.team-label-e2e.json -y
```

---

## 段階別結果 — L3 企画チーム

| # | step | 担当 | 結果 |
|---|------|------|------|
| 2 | asana_execute | asana-buddy | sync · fuzzy マッチ企画子 · 【2/2】create `1215081161914216` |
| 3 | pm_complete | planning-pm | comment `1215081151051577` → complete 企画子 |

```powershell
handoff_to_asana.py --handoff handoff.team-label-e2e.json `
  --require-review-result plan-review.team-label-e2e.json --if-not-exists -y
```

---

## 段階別結果 — L3 開発チーム

| # | step | 担当 | 結果 |
|---|------|------|------|
| 4 | dispatch | task-dispatcher | `DispatchRequest` task_gid=1215081161914216, department=development |
| 5 | 作業 | product-manager | 本記録作成 |
| 6 | pm_complete | product-manager | comment `1215080863974096` → complete 開発子 |

**チーム間入力:** 子 notes `チーム: development` のみ（Handoff JSON は読まない）

---

## 所見

1. **新規エピック作成** — bootstrap で親 + 企画子が `チーム:` 付きで作成された。
2. **sync + fuzzy マッチ** — bootstrap 企画子が【1/2】に対応付けられ、開発子が新規 create された。
3. **dispatch 互換** — `チーム: development` から開発チーム PM 起動可能。

---

## 完了状態

- [x] bootstrap 親 + 企画子
- [x] Handoff sync + 開発子 create
- [x] 企画子 complete（planning-pm）
- [x] 開発子 complete（product-manager）
- [x] 親エピック complete

## 関連

- [`planning-dept-v3-dryrun.md`](planning-dept-v3-dryrun.md)
- [`default-workflow.md`](../e2e/default-workflow.md)
- [`department-model.md`](../design/department-model.md)
