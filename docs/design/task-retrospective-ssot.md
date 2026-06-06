# タスク単位レトロ + エピック intake 起票 — 運用 SSOT

| 版 | 1.0 |
| 日付 | 2026-05-24 |
| エピック | `1215086241090085` · R1–R6 |

## 目的

- **各タスク complete 前** — エージェントが反省点・改善案を残す（知見の分散防止）
- **エピック complete 前** — 記録を集約し、**依頼者承認後のみ** intake 用 Asana タスクを起票

## 二層フロー

### A. タスク単位（L3 / L3b）

```
ワーカー作業完了
  → レトロ記録（必須 · R1）
       方式1: comment_task 本文に ## レトロスペクティブ + record_task_retrospective.py
       方式2: [retro] ネストサブ（create_retro_subtask.py）→ retro を comment → complete
  → comment_task（署名付き · レトロ節含む）
  → PM が当該サブ complete（check_task_retrospective.py 推奨）
```

### B. エピック単位（L1 workflow-orchestrator）

```
check_epic_audit_gate exit 0
  → aggregate_epic_retrospective.py
  → create_retrospective_intake_gate.py（**opt-in のみ**【承認】サブ · 候補一覧）
  → **opt-in 時:** 依頼者が Asana UI で complete（エージェント禁止）
  → check_retrospective_intake_gate.py exit 0（gate 無しも 0）
  → create_retrospective_intake_tasks.py（承認済み候補のみ · デフォルトは全候補）
  → comment_epic_summary.py → complete 親
```

## [retro] ネストサブ

| 項目 | 内容 |
|------|------|
| 命名 | `[retro] <worker_slug> — 所感・改善案` |
| 親 | worker サブタスク GID（ネスト · `addProject` 禁止） |
| notes | うまくいった点 / 改善したい点 / 次エピック候補 |
| CLI | [`create_retro_subtask.py`](../../skills/platform/asana-buddy/optional/create_retro_subtask.py) |

Phase 2: assign plan への [retro] 自動同梱。

## 成果物パス

| 種別 | パス |
|------|------|
| タスク単位 | `output/platform/retrospectives/<task_gid>-retro.json` |
| エピック集約 | `output/platform/retrospectives/<parent_gid>-epic-retro.json` |

## comment 必須節

[`agent-asana-comment-signature.md`](agent-asana-comment-signature.md) — ワーカー complete 前に `## レトロスペクティブ`（3 項目テンプレ）。

## 依頼者承認（intake 起票 · opt-in）

**デフォルト:** gate 無しで `create_retrospective_intake_tasks.py` が全候補を起票可。

**opt-in トリガー（いずれか）:**

- `create_retrospective_intake_gate.py --require-human-approval`
- retro JSON `human_retro_intake_gate: true`
- env `ORG_OPS_RETRO_INTAKE_GATE=1`
- epic notes `human_retro_intake_gate: yes`

- マーカー: `【承認】レトロ改善候補 → intake 起票`
- opt-in 時、未承認候補は Asana タスク化しない（epic-retro JSON にのみ残す）
- intake タスク notes に `## 依頼者コメント`（承認時の依頼者記入を反映）

## CLI 一覧

```powershell
python tools/record_task_retrospective.py --task <GID> --agent <slug> --went-well "..." --improve "..." --intake-candidate "..."
python tools/check_task_retrospective.py --task <GID>
python skills/platform/asana-buddy/optional/create_retro_subtask.py --parent <worker_sub> --worker <slug> -y
python tools/aggregate_epic_retrospective.py --parent <epic_gid>
python tools/create_retrospective_intake_gate.py --parent <epic_gid> --retro output/platform/retrospectives/<epic>-epic-retro.json -y
python tools/check_retrospective_intake_gate.py --parent <epic_gid>
python tools/create_retrospective_intake_tasks.py --parent <epic_gid> --retro <path> -y
```

## 参照

- [`workflow-io-contract.md`](workflow-io-contract.md)
- [`planning-gate-vs-pm-review-gate.md`](planning-gate-vs-pm-review-gate.md)
- [`pm-assign-review-gate.md`](pm-assign-review-gate.md)
