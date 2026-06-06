# PM review gate opt-in — delivery

| 項目 | 内容 |
|------|------|
| epic | `1215465361526049` |
| 開発子 | `1215465194255642` |
| intake | `1215465042124692` |

## 概要

PM assign-review gate を **デフォルト省略**。評価・監査時のみ opt-in で従来【レビュー】サブ構成・担当割り当てを作成。

## 変更ファイル

| ファイル | 変更 |
|----------|------|
| `tools/pm_review_gate_util.py` | `human_review_gate_requested` · `find_pm_assign_review_gate_sub` |
| `tools/create_pm_review_gate.py` | デフォルト SKIP · `--require-human-review` |
| `tools/check_pm_review_gate.py` | gate 無し exit 0 |
| `tools/execution_resume_scan.py` | assign gate タイトル限定 |
| `tools/test_pm_review_gate_opt_in.py` | unit test 新規 |
| `tools/validate_ssot_contract.py` | PM assignment doc 検査語更新 |
| `workflows/*-delivery.yaml` | `pm_review_gate` optional · `when: human_review_gate` |
| `docs/design/pm-assign-review-gate.md` | v1.3 opt-in SSOT |
| `docs/design/planning-gate-vs-pm-review-gate.md` | v1.3 デフォルト省略 |
| `docs/design/dispatch-prompt-ssot.md` | 5 PM 部門 intake 手順 |
| `docs/design/*-pm-assignment.md` | 5 本 PM assignment |
| `skills/platform/workflow-orchestrator/SKILL.md` | execution dispatch 説明 |

## opt-in トリガー

| 優先 | 手段 |
|------|------|
| 1 | assign plan `"human_review_gate": true` |
| 2 | `create_pm_review_gate.py --require-human-review` |
| 3 | env `ORG_OPS_PM_REVIEW_GATE=1` |
| 4 | PM 子 notes `human_review_gate: yes` |

## 検証

```powershell
python -m unittest tools.test_pm_review_gate_opt_in tools.test_runner_approval_helper_order -v
python tools/validate_ssot_contract.py
python tools/create_pm_review_gate.py --parent <PM子> --plan output/development/assign-plans/pm-review-gate-opt-in.lite.json -y
# → SKIP（gate 未作成）
python tools/check_pm_review_gate.py --parent <PM子>
# → exit 0
```

## 運用メモ

- planning gate 【承認】は従来どおり必須（変更なし）。
- PM 【レビュー】complete は引き続き人間のみ（`complete_task` exit 3）。
