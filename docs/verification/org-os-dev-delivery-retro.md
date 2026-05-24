# org-os + triage 開発子 — delivery 記録（正規ルート事後補完）

| 項目 | 内容 |
|------|------|
| 実施 | 2026-05-24 |
| 方針 | **正規 development-delivery lite** の事後補完（本体先行完了後） |
| 親エピック | `1215088809649925` |
| profile | lite（設計 skip） |

## 背景

【2/5】【3/5】について、初回は developer が PM / レビュー / QA フェーズを省略して親タスクを直接 complete した。利用者指示により **development-delivery v3 lite** に沿って証跡を後追い整備した。

## 開発子

| 子 | GID | 内容 |
|----|-----|------|
| 【2/5】triage | `1215102425337176` | workflow 拡張 · sync CLI |
| 【3/5】org-os | `1215088624074728` | 外部プロダクト scaffold |

## 正規フロー（実施内容）

1. `output/development/` に要件 · レビュー · 検証 · 事後仕様を作成
2. `pm_assign_subtasks.py` で lite assign plan から **7 サブ × 2** を Asana に作成
3. 各ワーカー slug で `comment_task.py` → `complete_task.py -y`（フェーズ順）
4. product-manager が親に DeptWorkComplete 相当コメントを投稿

### assign plan

| 親 | パス |
|----|------|
| 【2/5】 | `output/development/assign-plans/org-os-triage-2-5.lite.json` |
| 【3/5】 | `output/development/assign-plans/org-os-product-3-5.lite.json` |

### output/development 成果物

| 種別 | 【2/5】 | 【3/5】 |
|------|---------|---------|
| 要件 | `requirements/1215102425337176-requirements.md` | `requirements/1215088624074728-requirements.md` |
| 事後仕様 | `specs/1215102425337176-spec.md` | `specs/1215088624074728-spec.md` |
| 要件 review | `reviews/1215102425337176-requirements.review.json` | `reviews/1215088624074728-requirements.review.json` |
| code review | `reviews/1215102425337176-code.review.json` | `reviews/1215088624074728-code.review.json` |
| verification | `reviews/1215102425337176-verification.json` | `reviews/1215088624074728-verification.json` |
| mismatch | `reviews/1215102425337176-mismatch.review.json` | `reviews/1215088624074728-mismatch.review.json` |

## Asana 監査サブ（【2/5】）

| # | GID | 担当 | 状態 |
|---|-----|------|------|
| 1 | `1215089089686245` | requirements-writer | complete |
| 2 | `1215089026633101` | dev-reviewer | complete |
| 3 | `1215102426500444` | developer | complete |
| 4 | `1215089089741127` | dev-reviewer | complete |
| 5 | `1215088968942698` | qa-verifier | complete |
| 6 | `1215088969587775` | requirements-writer | complete |
| 7 | `1215088772906449` | dev-reviewer | complete |

## Asana 監査サブ（【3/5】）

| # | GID | 担当 | 状態 |
|---|-----|------|------|
| 1 | `1215102426056142` | requirements-writer | complete |
| 2 | `1215089026908632` | dev-reviewer | complete |
| 3 | `1215102425601682` | developer | complete |
| 4 | `1215102426500220` | dev-reviewer | complete |
| 5 | `1215088874237623` | qa-verifier | complete |
| 6 | `1215088873620630` | requirements-writer | complete |
| 7 | `1215088772756637` | dev-reviewer | complete |

## qa-verifier 実行コマンド

【2/5】:

```powershell
python tools/sync_org_os_cf_env.py --project 1214771428861230 --dry-run
python tools/intake_triage.py --snapshot output/platform/intake/1215086884850499-snapshot.json
python tools/auto_intake_runner.py --task 1215102364986845 --dry-run
python tools/validate_ssot_contract.py
```

【3/5】:

```powershell
python tools/org_os.py status --epic 1215088809649925
python tools/org_os.py watch --project 1214771428861230 --once
# dispatch --dry-run: legacy epic は os_state 未設定のため Ready チェックで exit 1（passed_with_notes）
```

## 再現コマンド

```powershell
# 1. output/development 成果物を用意（上表）
# 2. pm_assign
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent 1215102425337176 `
  --plan output/development/assign-plans/org-os-triage-2-5.lite.json `
  --department development --update-parent-assignee product-manager -y

# 3. 各サブ: comment_task（担当 slug）→ complete_task -y（フェーズ順）
# 4. PM 親コメント（product-manager slug）
```

## 教訓

1. gate 承認後の execution 系は **task-dispatcher → product-manager → pm_assign → ワーカー** が正規ルート。
2. 実装先行時も lite profile の **7 フェーズ証跡**を `output/development/` + Asana 監査サブで残す。
3. 次回以降は初回 complete 前に PM assign を実施する（本記録は事後補完）。

## 関連

- 初回 dryrun: [`org-os-triage-workflow-dryrun.md`](org-os-triage-workflow-dryrun.md) · [`org-os-product-dryrun.md`](org-os-product-dryrun.md)
- 先行例: [`asana-comment-detail-delivery.md`](asana-comment-detail-delivery.md)
- workflow: [`development-delivery.yaml`](../../workflows/development-delivery.yaml) v3 lite
