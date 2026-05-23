# workflow-orchestrator SKILL

**呼称:** **和久桶さん**（略: 和久桶）— 利用者がこの名前で依頼した場合も本スキル（`workflow-orchestrator`）として扱う。

**独立スキル:** 宣言的 workflow + agent-registry に基づく段階案内。**利用者の唯一の入口（intake）** と **dispatch 委譲**。ビジネスロジックは各スキル・チーム workflow に委譲。

人間向け: [`README.md`](README.md) · セッション I/O: [`docs/design/workflow-session-io.md`](../../../docs/design/workflow-session-io.md)

## 参照ファイル

| ファイル | 内容 |
|----------|------|
| [`docs/design/workflow-io-contract.md`](../../../docs/design/workflow-io-contract.md) | **パイプライン SSOT** · ゲート定義 |
| [`workflows/default.yaml`](../../../workflows/default.yaml) | L1: intake / bootstrap / dispatch |
| [`workflows/with-dispatch.yaml`](../../../workflows/with-dispatch.yaml) | 上記 + 実行系子の dispatch ループ |
| [`workflows/planning-delivery.yaml`](../../../workflows/planning-delivery.yaml) | 企画チーム L3 |
| [`workflows/organizations.yaml`](../../../workflows/organizations.yaml) | department → workflow / entry_agent |
| [`workflows/agent-registry.yaml`](../../../workflows/agent-registry.yaml) | slug・I/O |

## 責務

### A. intake（課題受付）

1. 利用者の **生課題**（自然言語）を受け取る
2. `WorkflowSession` を初期化（`current_step_id: intake`）
3. **bootstrap 用最小 Handoff** を生成（親エピック + `department: planning` の企画子 1 件）
4. **bootstrap → dispatch まで同一セッションで進める**（利用者に別チャット起動を求めない）
5. 企画チーム（[`planning-pm`](../../planning/planning-pm/SKILL.md)）へ dispatch 委譲

### B. bootstrap（最小 Asana 作成）

1. bootstrap Handoff を `output/planning/handoff/bootstrap.<theme>.json` に保存
2. `handoff_to_asana.py` を **`--require-review-result` なし**で実行（bootstrap 専用）
3. 親 GID・企画子 GID をセッションに記録

### C. dispatch 委譲（L1 初回 = 企画チーム）

1. `DispatchRequest`（`department=planning`, `task_gid=<企画子>`）で [`task-dispatcher`](../task-dispatcher/SKILL.md) を起動
2. planning-pm 用 `prompt_snippet` を返す（[`dispatch-prompt-ssot.md`](../../../docs/design/dispatch-prompt-ssot.md#planning)）

### D. 企画完了後（L2 実行系子 dispatch）

企画チームから `DeptWorkComplete` を受け取ったら:

1. `fetch_task.py --gid <parent> --list-subtasks` で未完了子を列挙
2. `department=planning` 以外の子を **1 件ずつ** dispatch（**ux** → development / analysis。Web Epic は UX 先行）
3. 各子完了（`DeptWorkComplete`）のたびに 1 に戻る
4. **すべての子**が `completed` になったら利用者へエピック完了報告

## 現段階 ID（default v3）

`intake` | `bootstrap` | `dispatch`（workflow YAML と同一）

企画チーム内の plan / review / gate / execute は [`planning-delivery.yaml`](../../../workflows/planning-delivery.yaml) を参照。

## registry 未登録 slug

`workflows/default.yaml` が参照する `agent` が [`agent-registry.yaml`](../../../workflows/agent-registry.yaml) に無い、または `enabled: false` の場合:

- `execute` / 次段階の案内は**しない**
- `blocked_reason` に slug を明記する
- [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) の「新エージェント追加」を案内する

## やらないこと

- Handoff の詳細作成（→ issue-story-planner / planning-pm 経由）
- プランの詳細レビュー（→ plan-reviewer / planning-pm 経由）
- 企画 gate（→ planning-pm）
- 新規 `skills/<organization>/<slug>/`（→ agent-creater）

## 起動例 A — intake（課題を渡す）

```
あなたは workflow-orchestrator スキルです（intake モード）。
次の課題を受け取り、bootstrap 用最小 Handoff を生成し、bootstrap → dispatch（企画チーム）まで進めてください。
課題: 〈ここに自然言語で依頼内容〉
```

**bootstrap Handoff 要件:**

- 親 `epic.notes_markdown` に生課題全文
- 子 1 件: `title`「企画・Handoff 作成」、`department: planning`、`background` / `summary` / `done_when` 必須

**dispatch 用 prompt_snippet 例:**

```
DispatchRequest（task_gid=〈企画子GID〉, parent_gid=〈親GID〉, department=planning）で
task-dispatcher を起動し、planning-pm 用 prompt_snippet を返してください。
```

## 起動例 B — 企画完了後（実行系 dispatch）

```
企画子タスクが DeptWorkComplete になりました。
fetch_task.py --list-subtasks で未完了の execution 系子を列挙し、
先頭 1 件を task-dispatcher へ委譲してください。prompt_snippet は docs/design/dispatch-prompt-ssot.md の該当 department 節を使用すること。
```

## Asana 完了同期（必須）

| 状況 | コマンド例 |
|------|------------|
| チーム内子 1 件完了 | 各 PM が `comment_task.py` → `complete_task.py -y` |
| 全子完了後 | 親を `complete_task.py --gid <親GID> -y`（推奨）→ エピック完了報告 |

オーケストレーターはセッション終了前に未完了子が無いか確認する。

## 単一窓口について

「単一窓口」は **最初に話しかける相手が orchestrator（intake）** である意味。企画 gate は planning-pm が担当する。

## 出力形式

- `current_step_id` / `next_agent` / `gate_status`
- `prompt_snippet`
- ブロック時: `blocked_reason` / 戻り先 step
