# product-manager 厳密運用 — チーム内アサインと delivery profile

| 版 | 1.5 |
| 日付 | 2026-06-11 |
| 適用 | 開発チーム L3（`development-delivery` v3） |

## 原則

1. **product-manager は自分で実装しない**（進行・委譲・完了集約を除く）。
2. PM が dispatch された子タスクを読み、**delivery profile** を決め、**workflow フェーズごとに作業単位を洗い出す**。
3. **必須:** 洗い出したフェーズを **Asana サブタスク** に分解し、各 notes に **担当 slug**（と必要なら `profile:`）を書く（親タスクへの単一 `担当:` 書き換えのみの委譲は禁止）。
4. **担当エージェントだけ**がそのサブタスクを実行する（notes の `担当:` と自分の slug が一致すること）。
5. 完了は **担当の comment_task → PM が当該サブを complete → 全サブ完了後に親を comment → complete**。

**comment_task:** PM slug で developer / dev-reviewer 等の作業を署名しない。実装作業は notes `担当:` のワーカー slug。

分析チーム同等運用: [`analytics-pm-assignment.md`](analytics-pm-assignment.md) · UX チーム: [`ux-pm-assignment.md`](ux-pm-assignment.md)

## PM の必須フロー（intake）

```
1. fetch_task.py --gid <親子GID> --show-assignee で notes を読む
2. delivery profile を決定（省略時 full）。full-ui は ## 依存（UX）を確認
3. profile に応じたフェーズ一覧を assign plan JSON に落とす
4. pm_assign_subtasks.py でサブタスク作成 + 各 担当: 設定
5. **デフォルト:** gate 省略 → **check_pm_review_gate.py** exit 0（gate 無し）→ L3b  
   **opt-in**（`human_review_gate: true` / `--require-human-review` / `ORG_OPS_PM_REVIEW_GATE=1`）: **create_pm_review_gate.py** → 人間 complete → check exit 0
6. 親 notes → 担当: product-manager, 状態: in_progress, profile: <決定値>
7. サブ完了のたびに次フェーズを確認し、全サブ完了後に DeptWorkComplete

**L3b:** 各サブについて [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md) に従い WorkerDispatchSnippet を別セッションへ渡す。PM が worker 成果物まで同一セッションで書かない。
```

**禁止:** サブタスクを作らず、親タスク notes の `担当:` だけ requirements-writer / developer 等に書き換えて委譲すること。

**dispatch 起動文 SSOT:** task-dispatcher は [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md#development) の snippet を **そのまま**返す。

## PM が書いてはいけない成果物（ワーカー専用）

| 種別 | パス | 担当 slug |
|------|------|-----------|
| 要件定義 | `output/development/requirements/<sub_gid>-requirements.md` | requirements-writer |
| 技術設計 | `output/development/design/<sub_gid>-design.md` | tech-designer |
| 実装 | `output/development/app/` ・別リポジトリ | developer |
| 事後仕様 | `output/development/specs/<sub_gid>-spec.md` | requirements-writer |
| 説明文書 | `output/development/documents/` · `output/platform/documents/` · `docs/inventory/`（catalog） | document-author |
| レビュー | `output/development/reviews/` | dev-reviewer / qa-verifier |
| UX 実装一致 | `output/ux/reviews/`（ux_implementation） | ux-reviewer |

PM が上記パスに直接書いた場合は **運用違反**。サブタスクを切り直し、該当ワーカーに差し戻す。

**PM が書いてよいもの:** 親子 notes · assign plan JSON · `comment_task` · DeptWorkComplete メタ。

**順序:** サブタスクは workflow 順（要件 → 設計 → 実装 → review → QA → 事後仕様）。前フェーズのゲート未通過のサブにはワーカーが着手しない。

## notes ヘッダ（必須・先頭）

### 親（進行タスク）

```markdown
チーム: development

profile: full-ui
担当: product-manager
状態: in_progress

```

### サブ（委譲タスク）

```markdown
チーム: development

profile: full-ui
担当: requirements-writer
状態: assigned

```

| フィールド | 値 |
|------------|-----|
| `チーム` | `development` |
| `profile` | `full` \| **`full-ui`** \| `lite` \| `doc-only`（親で決定。サブは省略可＝親継承） |
| `担当` | [`agent-registry.yaml`](../../workflows/agent-registry.yaml) の slug |
| `状態` | `assigned` \| `in_progress` \| `review` \| `done` |

その下に Handoff 由来の `## 背景` / `## 概要` / `## 完了条件` を置く。full-ui 親には `## 依存（読み取り専用）` を転記する。

## delivery profile

| profile | スキップする段階 | 備考 |
|---------|------------------|------|
| `full` | なし（ux_implementation 除く） | API / 非 UI |
| **`full-ui`** | なし | **`## 依存` に UX artifact 必須** |
| `lite` | tech-designer / design review | **画面タッチの子では禁止** |
| `doc-only` | 設計・実装・code/ux/verification review | **仕様整備**（requirements-writer 経路）。**読み手向け説明文書**だけなら `document-author` を assign（workflow step 外） |

### profile 選定ガイド（依頼文 → profile）

| 依頼のキーワード・状況 | 推奨 profile | 避ける profile |
|------------------------|--------------|----------------|
| org-meta · SSOT · SKILL · workflow YAML · 本リポジトリのみ | **doc-only** | full-ui |
| 依頼者向け企画書 · レポート · カタログのみ | **doc-only** + `担当: document-author` | requirements-writer 経路（仕様 AC 不要なら省略可） |
| 画面 · UI · Web · Figma · UX 仕様参照 | **full-ui**（UX 子完了後） | lite |
| API のみ · バックエンド · CLI · 小さな修正 | **full** または **lite** | full-ui |
| バグ修正 · 1 ファイル · 設計不要 | **lite**（非 UI のみ） | full-ui |

**判断の順序:** (1) 画面タッチか → full-ui / (2) コード実装か → full or lite / (3) 文書のみか → doc-only。

**スキル削除:** registry から slug を外す前に `grep` で参照ゼロ · `validate_org_registry.py` exit 0 を確認。削除は **段階的 deprecate**（inventory に Deprecated 注記）を推奨。新規 slug は **agent-creater** のみ。

### full-ui 着手チェック

- [ ] 同一 Epic の UX 子が Asana 上 **completed**
- [ ] notes に `## 依存（読み取り専用）` で UX 仕様パス **と Figma URL** がある
- [ ] `profile: full-ui` をヘッダに明記
- [ ] **`python tools/pm_intake_gate.py --gid <子GID> --plan <plan.json>` が exit 0**

未充足 → UX チームまたは企画 PM へ差し戻し。**developer へ委譲しない。**

`pm_assign_subtasks.py`（`--department development`）は **full-ui プラン時に上記を自動検証**し、未充足ならサブタスク作成前に停止する（`--skip-intake-gate` は緊急時のみ）。

### full-ui — UX 依存の転記（product-manager 必須）

UX 子完了後、**development 子の notes** に `## 依存（読み取り専用）` を追記してから intake を進める。

1. `fetch_task.py --gid <DEVELOPMENT_CHILD_GID>` で現 notes を確認
2. 転記元: UX 子の `DeptWorkComplete.artifacts[]` または ux-pm 完了コメント
3. notes 全文（ヘッダ + 既存 body + `## 依存` 表）を組み立て、`update_task_notes.py --notes @file.md -y` または `--preserve-body` 前に body に追記

依存表テンプレ: [`cross-team-artifact-bridge.md`](cross-team-artifact-bridge.md) · [`ux-delivery-io.md`](ux-delivery-io.md#下流開発チーム向け公開)

## サブタスク分解（例）

親: `【3/4・開発】Web アプリ API + 画面` — **担当: product-manager**（進行のみ） · **profile: full-ui**

| サブ | 担当 | 成果物 / ゲート |
|------|------|-----------------|
| 【3/4-1】要件定義 | requirements-writer | `output/development/requirements/<gid>-requirements.md` |
| 【3/4-2】要件 review | dev-reviewer | `review_kind: requirements` |
| 【3/4-3】技術設計 | tech-designer | `output/development/design/<gid>-design.md` |
| 【3/4-4】設計 review | dev-reviewer | `review_kind: design` |
| 【3/4-5】実装 | developer | コード |
| 【3/4-6】code review | dev-reviewer | `review_kind: code` |
| 【3/4-7】UX 実装一致 review | ux-reviewer | `review_kind: ux_implementation` |
| 【3/4-8】動作検証 | qa-verifier | `review_kind: verification` |
| 【3/4-9】事後仕様 | requirements-writer | `output/development/specs/<gid>-spec.md` |
| 【3/4-10】mismatch review | dev-reviewer | `review_kind: mismatch` |

**クロスチーム:** 【3/4-7】のサブ notes は `チーム: ux` · `担当: ux-reviewer`。L3b skill パスは registry 解決（`skills/ux/ux-reviewer/SKILL.md`）。

プラン例:

- `full-ui`: [`skills/development/examples/assign-plan.full-ui-v1.json`](../../skills/development/examples/assign-plan.full-ui-v1.json)
- `lite`（非 UI 小変更）: [`skills/development/examples/assign-plan.lite-v1.json`](../../skills/development/examples/assign-plan.lite-v1.json)
- `doc-only`: [`skills/development/examples/assign-plan.doc-only-v1.json`](../../skills/development/examples/assign-plan.doc-only-v1.json)
- `doc-only`（org-ops メタ doc）: [`skills/development/examples/assign-plan.org-meta-doc-v1.json`](../../skills/development/examples/assign-plan.org-meta-doc-v1.json)
- `doc-only`（workflow 見直し）: [`skills/development/examples/assign-plan.dev-workflow-review-v1.json`](../../skills/development/examples/assign-plan.dev-workflow-review-v1.json)

`lite` / `doc-only` は設計・実装サブを省略。`doc-only` は verification / ux_implementation も省略。

## 委譲先一覧（v3）

| 段階 | 担当 slug | サブタスク |
|------|-----------|------------|
| 要件定義 | requirements-writer（mode=requirements） | 必須 |
| 要件 review | dev-reviewer | 必須 |
| 技術設計 | tech-designer | full / full-ui のみ |
| 設計 review | dev-reviewer | full / full-ui のみ |
| 実装 | developer | full / full-ui / lite |
| code review | dev-reviewer | full / full-ui / lite |
| UX 実装一致 review | **ux-reviewer** | **full-ui のみ** |
| 動作検証 | qa-verifier | full / full-ui / lite |
| 事後仕様 | requirements-writer（mode=as-built-spec） | 必須 |
| mismatch | dev-reviewer | 必須 |

## CLI

```powershell
# notes 更新（担当追記）
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\update_task_notes.py `
  --gid <GID> --department development --assignee tech-designer --status assigned --preserve-body -y

# チーム内サブタスク一括作成（JSON プラン）
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent <親GID> --plan .\skills\development\examples\assign-plan.full-ui-v1.json `
  --department development --update-parent-assignee product-manager -y

# 担当確認（ワーカー着手前必須）
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <GID> --show-assignee

# サブタスク一覧
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\fetch_task.py --gid <親GID> --list-subtasks
```

## レビュー NG 時（修正タスク）

[`pm-review-rework-ssot.md`](pm-review-rework-ssot.md) — **推奨 CLI:**

```powershell
python tools/pm_create_fix_subtask.py --parent <親GID> --review-json output/development/reviews/<file>.json -y
python tools/pm_create_fix_subtask.py --parent <親GID> --review-json <path> --emit-dispatch -y
```

## 実行エージェントの起動例

```
あなたは developer スキルです。Asana サブタスク GID ○○ の notes を読み、
fetch_task.py --show-assignee で担当が developer であることを確認してから作業し、
完了前に comment_task.py を実行してください。
```

## 参照

- **dispatch prompt:** [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md#development)
- **worker dispatch:** [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md)
- **review NG → 修正タスク:** [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)
- [`development-delivery-io.md`](development-delivery-io.md)
- [`ux-delivery-io.md`](ux-delivery-io.md)
- [`development-delivery.yaml`](../../workflows/development-delivery.yaml)
- [`skills/development/product-manager/SKILL.md`](../../skills/development/product-manager/SKILL.md)
