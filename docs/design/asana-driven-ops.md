# Asana ドリブン運用 — org-ops SSOT（Phase 1–3）

| 版 | 1.3 |
| 日付 | 2026-05-24 |
| Phase 1 エピック | `1215101833446108` |
| Phase 2 エピック | `1215087157303128` |
| Phase 3 エピック | `1215087157410286` |
| Phase 4 エピック | `1215087317688245` |
| ブランチ | `feature/asana-driven-ops` |

## 目的

Asana を運用ダッシュボードとして、**AI タスク検出 → intake → 人間承認 → エージェント再開** をチャット依存なく追跡する。Phase 1 は **CLI ポーリング MVP**（Webhook / ダッシュボードは Phase 2+）。

## コンポーネント

| コンポーネント | パス | 役割 |
|----------------|------|------|
| スキャン / ポーラ | [`tools/asana_ops_poller.py`](../../tools/asana_ops_poller.py) | プロジェクト走査 · intake トリガー · 保留監視 · **Phase 2:** `--projects` |
| 保留確認 | [`tools/check_workflow_suspend.py`](../../tools/check_workflow_suspend.py) | suspended 一覧 / gate 状態 · resumable hint |
| RESUME snippet | [`tools/pm_emit_resume_prompt.py`](../../tools/pm_emit_resume_prompt.py) | **Phase 2** — gate complete 後の再開プロンプト |
| sessions 共有 | [`tools/asana_ops_sessions.py`](../../tools/asana_ops_sessions.py) | **Phase 3** — session JSON · webhook ログ |
| Webhook dryrun | [`tools/asana_webhook_handler.py`](../../tools/asana_webhook_handler.py) | **Phase 3** — POST /webhook · complete 検知 |
| ダッシュボード | [`tools/asana_ops_dashboard.py`](../../tools/asana_ops_dashboard.py) | **Phase 3** — WAIT/RESUME 一覧 UI（port 8765） |
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
| `DISPATCH` | intake / bootstrap 後の次アクション hint（orchestrator / PM 起動プロンプト） |
| `WAIT` | 人間 gate 待ち（**`--record-wait` 保存済み** · ダッシュボード表示） |
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

- ~~マルチプロジェクト横断スキャン~~ → **Phase 2 で実装**（`--projects`）
- ~~Asana Webhook 本番~~ → **Phase 3 で dryrun 実装**（本番 SLA は非スコープ）
- セッション永続化の Cursor ネイティブ統合
- `--trigger-intake` からの完全自動 bootstrap（snapshot + 起動ヒントのみ）

---

## Phase 2 追記（2026-05-24 · エピック `1215087157303128`）

### 追加 CLI

```powershell
# マルチプロジェクト
python tools/asana_ops_poller.py --once --projects 1214771428861230,<OTHER>

# PM review gate 保留
python tools/asana_ops_poller.py --record-wait <親GID> <【レビュー】GID> <URL> \
  --gate-kind pm_review_gate --department development

# RESUME 後 snippet
python tools/pm_emit_resume_prompt.py --list
python tools/pm_emit_resume_prompt.py --session <session_id_prefix>
```

### gate_kind

| gate_kind | marker | record-wait |
|-----------|--------|-------------|
| `planning_approval` | 【承認】 | デフォルト |
| `pm_review_gate` | 【レビュー】 | `--gate-kind pm_review_gate --department <dept>` |

`RESUME` 検知時 `--human` で `pm_emit_resume_prompt` snippet を stderr に出力。

### dryrun

[`asana-driven-ops-phase2-dryrun.md`](../verification/asana-driven-ops-phase2-dryrun.md)

### UX

`output/ux/specs/1215087017928843-ux-spec.md`

---

## Phase 3 追記（2026-05-24 · エピック `1215087157410286`）

### 追加 CLI

```powershell
# Webhook handler（別ターミナル）
python tools/asana_webhook_handler.py --port 8766

# ダッシュボード
python tools/asana_ops_dashboard.py --port 8765

# Webhook テスト POST
curl -X POST http://127.0.0.1:8766/webhook -H "Content-Type: application/json" ^
  -d "{\"events\":[{\"action\":\"changed\",\"resource\":{\"gid\":\"SUB_GID\",\"resource_type\":\"task\"},\"change\":{\"field\":\"completed\",\"new_value\":true}}]}"
```

### poller 併用方針

| 方式 | 用途 |
|------|------|
| **Webhook** | リアルタイム RESUME 検知（優先 · dryrun） |
| **poller** | fallback · マルチプロジェクト SCAN · intake |

両方とも `output/platform/sessions/` を共有。ダッシュボードは `/api/sessions` で一覧表示。

### dryrun

[`asana-driven-ops-phase3-dryrun.md`](../verification/asana-driven-ops-phase3-dryrun.md)

### UX

`output/ux/specs/1215087283197185-ux-spec.md`

---

## Phase 4 追記（2026-05-24 · エピック `1215087317688245`）

### 目的

条件を満たす Asana タスクを検出し、**和久桶さん（workflow-orchestrator）intake** までを段階的に自動化する。**CLI baseline 必須** · **Cursor SDK optional**。

### 検出条件

| # | 条件 | Phase |
|---|------|-------|
| 1 | `completed = false` | 1 |
| 2 | CF 担当種別 = `AI` | 1 |
| 3 | スキャン対象プロジェクト（`ASANA_PROJECT_ID` または `--projects`） | 2 |
| 4 | 未 intake（`INTAKE_MARKER` story なし · epic 名 `【org-ops】` 除外） | 1 |
| 5 | **拡張フック（将来）** — タイトル prefix · セクション · 追加 CF | 4+ |

### 二経路

| 経路 | 手段 | 必須 |
|------|------|------|
| **CLI baseline** | `intake_from_asana` → bootstrap Handoff → `handoff_to_asana`（review なし）→ planning dispatch | **はい** |
| **CLI 実装** | [`tools/auto_intake_runner.py`](../../tools/auto_intake_runner.py) · poller `--auto-bootstrap` | 子【2/5】 |
| **Cursor SDK** | `Agent.prompt` / `Agent.create` で orchestrator intake-asana プロンプト起動 | optional（PoC 子【3/5】） |

### フロー D. auto-intake（Phase 4）

```
asana_ops_poller --once
  → CANDIDATE
  → INTAKE（snapshot）
  → AUTO_BOOTSTRAP（--auto-bootstrap · 実装は子【2/5】）
  → planning: Handoff · review · gate
  → --record-wait（planning_approval）   ← ダッシュボード WAIT 必須
  → 依頼者【承認】complete
  → RESUME → handoff_to_asana --require-review-result
  → execution dispatch（task-dispatcher → 各 PM）
```

**PM review gate** も `--record-wait --gate-kind pm_review_gate --department <dept>` でダッシュボードに反映する。

### planning gate とダッシュボード

| 段階 | 必須操作 | ダッシュボード |
|------|----------|----------------|
| planning 【承認】作成後 | `asana_ops_poller --record-wait <親> <承認サブ> <URL>` | WAIT 表示 |
| PM 【レビュー】作成後 | `--record-wait ... --gate-kind pm_review_gate --department development` | WAIT 表示 |
| 【承認】/【レビュー】complete | poller `RESUME` · `pm_emit_resume_prompt` | RESUME 表示 |

**注意:** 【承認】/【レビュー】サブ作成だけではダッシュボードに載らない。必ず `--record-wait` で `output/platform/sessions/` に保存する。

**gate 到達時チェックリスト（§H）:** [`workflow-orchestrator/SKILL.md`](../../skills/platform/workflow-orchestrator/SKILL.md) §H — planning gate / PM review gate 到達時の必須手順。

### 安全弁

- `--auto-bootstrap` は **dry-run 既定** · `-y` で opt-in
- 重複 intake: 既存 `already_intake_source` / epic リンク story
- CF PUT 400: 警告のみ · 処理継続（[`asana-assignee-type-field.md`](asana-assignee-type-field.md)）
- 手動 intake-asana（チャット URL 渡し）は **併存維持**

### 非スコープ（Phase 4 · SSOT 段階）

- ~~`--auto-bootstrap` / `auto_intake_runner.py` 実装~~ → **子【2/5】で実装**
- Cursor SDK PoC 実装（子【3/5】）
- Webhook 本番 SLA

### CLI（子【2/5】）

```powershell
python tools/auto_intake_runner.py --task <SOURCE_GID> --dry-run
python tools/auto_intake_runner.py --task <SOURCE_GID> -y
python tools/asana_ops_poller.py --once --auto-bootstrap --dry-run
python tools/asana_ops_poller.py --once --auto-bootstrap -y
```

### dryrun（予定）

[`asana-driven-auto-intake-dryrun.md`](../verification/asana-driven-auto-intake-dryrun.md)（子【5/5】）

## 参照

- UX: `output/ux/specs/1215086510974424-ux-spec.md`
- development dryrun: [`asana-driven-ops-dryrun.md`](../verification/asana-driven-ops-dryrun.md)
- 担当種別 CF: [`asana-assignee-type-field.md`](asana-assignee-type-field.md)
