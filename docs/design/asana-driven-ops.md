# Asana ドリブン運用 — org-ops SSOT（Phase 1）

| 版 | 1.0 |
| 日付 | 2026-05-24 |
| エピック | `1215101833446108` |
| ブランチ | `feature/asana-driven-ops` |

## 目的

Asana を運用ダッシュボードとして、**AI タスク検出 → intake → 人間承認 → エージェント再開** をチャット依存なく追跡する。Phase 1 は **CLI ポーリング MVP**（Webhook / ダッシュボードは Phase 2+）。

## コンポーネント

| コンポーネント | パス | 役割 |
|----------------|------|------|
| スキャン / ポーラ | [`tools/asana_ops_poller.py`](../../tools/asana_ops_poller.py) | プロジェクト走査 · intake トリガー · 保留監視 |
| 保留確認 | [`tools/check_workflow_suspend.py`](../../tools/check_workflow_suspend.py) | `output/platform/sessions/` の suspended 一覧 / gate 状態 |
| intake snapshot | [`tools/intake_from_asana.py`](../../tools/intake_from_asana.py) | Asana タスク → snapshot JSON |
| 承認サブ作成 | [`create_approval_subtask.py`](../../skills/platform/asana-buddy/optional/create_approval_subtask.py) | 【承認】/【レビュー】汎用 |
| 承認 polling | [`check_approval_subtask.py`](../../skills/platform/asana-buddy/optional/check_approval_subtask.py) | サブ complete 検知 |

## CLI 出力語彙（UX SSOT）

| 行頭 | 意味 |
|------|------|
| `SCAN` | プロジェクト走査開始 |
| `SKIP` | 候補除外（完了済み · 重複 intake · CF 不一致等） |
| `CANDIDATE` | intake 候補タスク |
| `INTAKE` | snapshot / trigger 実行 |
| `WAIT` | 人間 gate 待ち（保留セッション保存または継続待機） |
| `RESUME` | gate complete 検知 — dispatch 再開可 |

## スキャン条件（MVP）

1. `completed = false`
2. CF 担当種別 = `AI`（[`asana-assignee-type-field.md`](asana-assignee-type-field.md)）
3. 同一 `ASANA_PROJECT_ID`（横断は Phase 2）
4. intake 済みでない（source complete または epic リンク story ありは除外）

## 保留 / 再開（Phase 1）

### セッション JSON

保留時、オーケストレーターは [`workflow-session-io.md`](workflow-session-io.md) の **SuspendedSession** を `output/platform/sessions/<session_id>.json` に保存する。

```powershell
python tools/asana_ops_poller.py --record-wait <親GID> <承認サブGID> <承認サブURL>
```

`gate_kind` 例: `planning_approval` · `pm_review_gate`（Phase 2 で拡張）

### 再開検知

```powershell
python tools/asana_ops_poller.py --once          # WAIT / RESUME 行を出力
python tools/check_workflow_suspend.py --list    # 保留一覧
python tools/check_workflow_suspend.py --all --require-resumable  # CI / 手動再開前
```

`RESUME` 検知後、**新規 Cursor セッション**で task-dispatcher / 該当 PM へ dispatch する（同一セッション継続は Phase 2）。

## フロー

### A. 自動 intake（MVP）

```
asana_ops_poller --once
  → CANDIDATE（未完了 · AI · 未 intake）
  → intake_from_asana（--trigger-intake は snapshot のみ · bootstrap は別セッション）
  → bootstrap → plan-review → planning-pm が【承認】サブ作成
  → --record-wait → セッション終了（suspended）
  → 依頼者が【承認】complete
  → poller: RESUME → handoff_to_asana / dispatch 続行
```

### B. PM review gate（既存 · 継続）

[`pm-assign-review-gate.md`](pm-assign-review-gate.md) — `create_pm_review_gate.py` → 【レビュー】complete → L3b dispatch。

planning gate との違い: [`planning-gate-vs-pm-review-gate.md`](planning-gate-vs-pm-review-gate.md)

### C. 手動 intake（維持）

Asana URL/GID をチャットまたは CLI で和久桶に渡す。自動スキャンと **併存**。

## planning gate Asana 化（Phase 1 手順）

1. planning-pm: `plan-reviewer` 通過後、`create_approval_subtask.py` で企画子または親に **【承認】** サブを作成（notes に Handoff 要約）
2. workflow-orchestrator: チャット承認の代わりに **`--record-wait`** で保留 JSON を保存しセッション終了
3. 依頼者: Asana UI で【承認】サブを **complete**
4. 運用者: `asana_ops_poller --once` で `RESUME` 確認 → 新セッションで `handoff_to_asana.py --require-review-result`

**注意:** チャットの「承認」「すすめて」は planning gate の **フォールバック** として残るが、Asana ドリブン運用では【承認】サブ complete を正とする。

## 非スコープ（Phase 1）

- マルチプロジェクト横断スキャン
- Asana Webhook 本番
- セッション永続化の Cursor ネイティブ統合
- `--trigger-intake` からの完全自動 bootstrap（snapshot のみ）

## 参照

- UX: `output/ux/specs/1215086510974424-ux-spec.md`
- development dryrun: [`asana-driven-ops-dryrun.md`](../verification/asana-driven-ops-dryrun.md)
- 担当種別 CF: [`asana-assignee-type-field.md`](asana-assignee-type-field.md)
