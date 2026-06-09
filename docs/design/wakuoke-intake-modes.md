# 和久桶さん intake モード — SSOT

| 版 | 1.0 |
| 日付 | 2026-06-09 |
| 状態 | **本番標準** |
| SSOT id | `wakuoke-intake-modes` |
| 親 SSOT | [`chat-driven-ops.md`](chat-driven-ops.md) |

## 目的

和久桶さん（`workflow-orchestrator`）の **依頼受付（intake）に幅を持たせる**。依頼の性質に応じて入口を選びつつ、**企画 → gate → Asana 投入 → execution dispatch** の正規パイプラインは維持する。

## 三つの intake モード

| モード | `intake_mode` | いつ使う | intake | bootstrap | 以降 |
|--------|---------------|----------|--------|-----------|------|
| **A. 課題受付** | `natural_language`（既定） | 簡単な依頼・機能追加・組織変更 | 生課題を受け取り方針提示 | 親 Epic + 企画子 1 件 | planning → execution dispatch |
| **B. タスク作成依頼** | `task_creation_request` | タスク化の相談・起票方針の相談 | 相談内容を整理し Epic 構成を合意 | 合意後に Epic + 子を起票 | planning（必要時）→ dispatch |
| **C. Epic インプット** | `epic_input` | **既存 Epic** を渡して遂行再開 | **省略**（Epic は既存） | **省略** | 状態確認 → dispatch（企画 or execution） |

### 共通原則

- **禁止:** Handoff · plan-reviewer · gate · Asana 投入を経ずに registry / skills / workflow / 成果物本体を直接編集すること（[`workflow-intake-required.mdc`](../../.cursor/rules/workflow-intake-required.mdc)）。
- **Asana タスク運用**（作成 · 遂行 · comment / complete）は継続。**Asana 自動化**（無人検出 · watch）は廃止のまま。
- 同一セッションで **利用者に別チャット起動を求めない**。

---

## A. 課題受付（既定 · `natural_language`）

**用途:** 簡単な依頼内容から企画し Epic に落とし込む。

```
依頼者 ──チャット──► 和久桶（intake）
  → bootstrap（Asana 親 Epic + 企画子）
  → dispatch → planning-pm
      → issue-story-planner → plan-reviewer
      → gate → handoff_to_asana（実行系子）
  → task-dispatcher → 各 PM L3
```

**手順:**

1. 自然言語で生課題を受け取る
2. 方針を一言提示（intake → bootstrap → 企画 → execution）
3. bootstrap 用最小 Handoff を生成（親 + `department: planning` 子 1 件）
4. `handoff_to_asana.py` で Epic 起票
5. planning-pm へ dispatch

**任意変種 — intake-asana:** チャットで Asana タスク URL/GID を添付した場合は `intake_mode: asana_task`。snapshot → triage → bootstrap（[`workflow-orchestrator/SKILL.md`](../../skills/platform/workflow-orchestrator/SKILL.md) §A）。

---

## B. タスク作成依頼（`task_creation_request`）

**用途:** 和久桶さんに **タスク化の相談** をした場合。相談内容を整理し **Epic に落とし込んで起票** する。

**A との違い:**

| 観点 | A 課題受付 | B タスク作成依頼 |
|------|------------|------------------|
| 依頼の焦点 | 課題・成果そのもの | **どうタスクに分けるか** · 起票の仕方 |
| intake での対話 | 最小（方針提示で進行） | **スコープ · 子の department · マイルストーン** を短く合意 |
| bootstrap Handoff | 企画子 1 件のみ | 企画子 + **想定マイルストーン**（`[MSn]` トラッカー案）を notes に記載可 |
| planning | 必須（Handoff 詳細化） | 子構成が明確なら Handoff を厚めにし planning を短縮可 |

**手順:**

1. 相談内容（「この作業をタスクにしたい」「Epic の切り方」等）を受け取る
2. **Epic タイトル · 想定子（department）· マイルストーン案** をチャットで提示し合意
3. bootstrap Handoff を生成 — `epic.notes_markdown` に合意内容 · マイルストーン案を記載
4. Epic + 企画子を起票 → planning-pm dispatch
5. 企画で Handoff 詳細化 → 実行系子 · **マイルストーン tracker 子** を `asana_execute` で投入

**起動例:**

```
和久桶さん、次をタスク化の相談です（タスク作成依頼）。

〈相談内容〉

Epic 構成とマイルストーン案を提示し、合意後に bootstrap → 起票まで進めてください。
```

---

## C. Epic インプット（`epic_input`）

**用途:** **intake を省略**し、渡された **既存 Epic** をディスパッチしてタスク遂行する。

**前提:** Asana 上に親 Epic（Task Type=Epic）が既に存在すること。

**手順:**

1. 依頼者から **親 Epic の URL / GID** を受け取る
2. `fetch_task.py --gid <親> --list-subtasks` で子の状態を確認
3. 分岐:

| Epic の状態 | 次のアクション |
|-------------|----------------|
| 企画子のみ · 未完了 | `DispatchRequest(department=planning)` → planning-pm |
| 企画完了 · execution 系子あり | 未完了子を列挙 → task-dispatcher（L2 自動進行） |
| 全子完了 | マイルストーン締め · レトロ · 親 complete 手順へ |

4. `WorkflowSession` は `current_step_id: dispatch` · `parent_gid` 設定で開始（bootstrap スキップ）

**起動例:**

```
和久桶さん、Epic インプットです（intake 省略）。

親 Epic: 〈URL または GID〉

子タスクの状態を確認し、未完了分を dispatch して遂行を進めてください。
```

**禁止:** Epic が存在しないのに bootstrap を飛ばして成果物を直接書くこと。

---

## Epic マイルストーンと着実な進行

Epic 遂行では **マイルストーンを設定し、節目ごとに着実に対応を進める** ことを標準とする。

### マイルストーンの設定（企画 · bootstrap 時）

- issue-story-planner / planning-pm が Handoff に **`[MS1]` `[MS2]` … トラッカー子**（`department: governance`）を含める
- ロードマップ Epic では `[M4]`–`[M9]` 等の節目トラッカーも同様（[`completion-100-roadmap`](../../docs/verification/governance/completion-100-roadmap-intake.md)）
- 各トラッカーの `done_when` は **名目** と **実効** の二層（[`milestone-effectiveness-standard.md`](milestone-effectiveness-standard.md)）

### 各マイルストーンでの自己評価（組織体制構築済）

マイルストーン自律評価の仕組みは **2026-06-09 時点で組織構築済**（Epic `1215534306691804` · MS1–MS5 完了）。

| タイミング | 必須アクション |
|------------|----------------|
| 作業 Epic の子が揃った後 | `check_milestone_readiness.py` / `emit_milestone_effectiveness_report.py` |
| トラッカー complete 前 | `epic_milestone_readiness_hook.py` |
| スコア不足時 | `create_milestone_followup_subtasks.py` でフォローアップ子起票 |

詳細: [`skills/governance/governance-pm/SKILL.md`](../../skills/governance/governance-pm/SKILL.md) · [`workflow-orchestrator/SKILL.md`](../../skills/platform/workflow-orchestrator/SKILL.md) §D

### 出来栄えの目標スコア

| 対象 | 目標 | 機械閾値（complete 可否） |
|------|------|---------------------------|
| **各マイルストーン**（中間 `[MSn]`） | **90 点以上を目指す** | ≥ 80 で complete 可（< 70 は禁止） |
| **最終マイルストーン**（Epic 完了前の最終 `[MSn]` または成果物納品） | **90 点以上を達成する**（必須） | **≥ 90 未満ではトラッカー complete 禁止** |

- 中間マイルストーン: 90 未満でも 80 以上なら complete 可だが、**ギャップと改善案を comment** し次マイルストーンで吸収する
- 最終マイルストーン: `min_score_achieved: 90` を checklist fixture に指定（[`milestone-effectiveness-standard.md`](milestone-effectiveness-standard.md) §閾値）
- 成果物納品の完成度は [`delivery-completion-standard.md`](delivery-completion-standard.md)（80% 必須条件）と併用

---

## モード判定（エージェント）

依頼文のキーワードで初期 `intake_mode` を推定する。曖昧ならチャットで 1 問確認。

| シグナル | モード |
|----------|--------|
| 「タスク化」「起票の相談」「Epic の切り方」 | `task_creation_request` |
| Epic URL/GID + 「インプット」「遂行」「再開」「dispatch のみ」 | `epic_input` |
| 上記以外（「お願いします」「作って」「課題」） | `natural_language` |

---

## セッション I/O

[`workflow-session-io.md`](workflow-session-io.md) の `intake_mode` 列挙を参照。

| モード | `current_step_id` 初期値 | `parent_gid` |
|--------|--------------------------|--------------|
| A / B | `intake` | bootstrap 後に設定 |
| C | `dispatch` | 依頼時に設定 |

---

## 関連

| 文書 | 内容 |
|------|------|
| [`chat-driven-ops.md`](chat-driven-ops.md) | チャット入口 SSOT |
| [`workflow-io-contract.md`](workflow-io-contract.md) | パイプライン全体 |
| [`milestone-effectiveness-standard.md`](milestone-effectiveness-standard.md) | 実効スコア · 閾値 |
| [`workflow-orchestrator/SKILL.md`](../../skills/platform/workflow-orchestrator/SKILL.md) | 手順・コマンド |

## 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-06-09 | v1.0 — 三モード（課題受付 · タスク作成依頼 · Epic インプット）とマイルストーン 90 点目標を明文化 |
