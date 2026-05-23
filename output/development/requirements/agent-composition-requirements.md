# 要件定義書 — エージェント構成とワークフロー

| 項目 | 内容 |
|------|------|
| 文書種別 | 要件定義書（requirements-doc） |
| 作成者ロール | product-manager |
| 対象 | agent-create-supporter リポジトリ全体のマルチエージェント構成 |
| 参照 workflow | `default` v3 · `planning-delivery` · `with-dispatch` · `ux-delivery` · `development-delivery` · `analysis-delivery` |
| 版 | 1.4 |
| 日付 | 2026-05-23 |

---

## 1. 背景と目的

### 1.1 背景

本リポジトリは、Cursor / Copilot 上で動作する**スキルベースのエージェント群**を Git 共有し、次の流れを実現する。

1. 利用者が自然言語で課題を提示する
2. 企画（ストーリー・タスク案）→ レビュー → Asana タスク化まで行う
3. Asana 上の**子タスクごと**に、適切な**チーム**へ配賦し、開発・文書・レビューを進める

従来は `task-executor` が子タスクを単独で処理していた。組織配賦コミット（`7f91132`）以降、**開発チームは PM ハブ + 専門ロール**へ移行する。

### 1.2 目的

- 利用者が**スキル名を覚えず**、オーケストレーターに話しかけるだけで企画〜実行に進める
- 企画品質を `plan-reviewer` で担保してから Asana 投入する
- **子タスク 1 件 = 配賦 1 回 = チーム内ワークフロー 1 本**で、開発・分析が混在するエピックを扱える
- 新規エージェント追加時に workflow / registry を拡張し、オーケストレーターを肥大化させない

### 1.3 スコープ

| 含む | 含まない |
|------|----------|
| 全業務スキル・メタスキルの役割と連携 | Asana ワークスペースの人事・アサイン実務 |
| L1 企画 / L2 配賦 / L3 チーム内の責務 | workflow YAML の実行エンジン実装 |
| Handoff・レビュー・配賦・完了報告の I/O | 分析パイプライン・モデルの**製品コード**（別リポジトリ） |
| 過渡期の `task-executor` | 外部 SaaS（Notion 等）連携 |

---

## 2. ステークホルダーと利用者像

| 役割 | ニーズ |
|------|--------|
| **利用者（依頼者）** | 自然言語のみで依頼。企画書（Asana）と実行結果を得たい |
| **オーケストレーター** | 入口・bootstrap・dispatch 委譲・エピック完了の集約 |
| **企画チーム（planning-pm / planner / reviewer）** | Handoff・品質レビュー・gate・Asana タスク化 |
| **タスクディスパッチャー** | 子タスクをチームへルーティング |
| **開発チーム PM** | 子 1 件のライフサイクル管理 |
| **開発チームメンバー** | 要件・設計・実装・レビュー・検証（v2 6 ロール） |
| **asana 管理者** | タスク CRUD・読取・完了マーク（統括グループ） |
| **agent-creater** | 新規スキル雛形の唯一の生成入口 |

---

## 3. 機能要件

### 3.1 L1 — 受付フェーズ（workflow: `default` v3）

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-L1-01 | 利用者は **workflow-orchestrator（intake）** を唯一の入口とする | 必須 |
| FR-L1-02 | orchestrator は生課題を受け、**bootstrap 用最小 Handoff**（企画子 1 件）を生成する | 必須 |
| FR-L1-03 | **asana-buddy（bootstrap）** は親 + 企画子 1 件を Asana に作成する | 必須 |
| FR-L1-04 | orchestrator は **task-dispatcher** 経由で企画子を **planning-pm** へ配賦する | 必須 |

### 3.2 L3 — 企画チーム（workflow: `planning-delivery`）

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-L3P-01 | **issue-story-planner** は **AsanaBuddyHandoff**（v1.1/v1.2）を 1 件出力する | 必須 |
| FR-L3P-02 | **plan-reviewer** によるレビューは省略不可 | 必須 |
| FR-L3P-03 | **planning-pm（gate）** は review 結果を確認し、人間承認後に Asana 投入する | 必須 |
| FR-L3P-04 | **asana-buddy** は承認済み Handoff から親更新 + execution 系子タスクを作成する | 必須 |
| FR-L3P-05 | CLI 投入時は `--require-review-result` で review ゲートを強制できる | 推奨 |
| FR-L3P-06 | v1.2 では execution 系子タスクに `department` を付与できる | 推奨 |

**ゲート（企画チーム内）**

- `review_passed`: 未達時は asana_execute 不可
- `handoff_approved`: 人間が planning-pm 経由で Asana 投入を許可

### 3.3 L2 — 配賦フェーズ（workflow: `with-dispatch` v2）

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-L2-01 | 企画完了後、**execution 系子タスク 1 件単位**で実行依頼を受け付ける | 必須 |
| FR-L2-02 | orchestrator は未完了子を列挙し、**task-dispatcher** へ委譲する | 必須 |
| FR-L2-03 | dispatcher は `department` に基づきチーム workflow の **entry_agent** へルーティングする | 必須 |
| FR-L2-04 | ルーティング表は `workflows/organizations.yaml` に宣言的に定義する | 必須 |
| FR-L2-05 | `department=planning` のとき **planning-pm** を起動する | 必須 |
| FR-L2-06 | `department=development` のとき **product-manager** を起動する | 必須 |
| FR-L2-07 | `department=analysis` のとき **analytics-pm** を起動する | 必須 |
| FR-L2-09 | `department=ux` のとき **ux-pm** を起動する | 必須 |
| FR-L2-08 | `department` 未設定時は Handoff の `pillar` または Asana notes の `チーム:` 行から推定する | 推奨 |

### 3.3 L3 — 開発チームフェーズ（workflow: `development-delivery` v3）

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-L3-01 | PM は子タスク notes（背景・概要・完了条件・**profile**）を読み、**delivery profile**（`full` / **`full-ui`** / `lite` / `doc-only`）を決定する | 必須 |
| FR-L3-02 | **requirements-writer** が要件定義書を作成し、**dev-reviewer** がレビューする | 必須 |
| FR-L3-03 | profile=`full` 時、**tech-designer** が技術設計書を作成し、**dev-reviewer** がレビューする（`lite` / `doc-only` は skip） | 必須 |
| FR-L3-04 | 要件・設計 OK 後、PM は **developer** に実装を依頼する（`doc-only` は skip） | 必須 |
| FR-L3-05 | **dev-reviewer** がコードレビューを行う | 必須 |
| FR-L3-06 | **qa-verifier** が動作検証を行う（developer / dev-reviewer と独立） | 必須 |
| FR-L3-07 | PM は **requirements-writer**（mode=as-built-spec）に事後詳細仕様書作成を依頼する | 必須 |
| FR-L3-08 | **dev-reviewer** は要件定義書と事後詳細仕様の**整合レビュー**を行う | 必須 |
| FR-L3-09 | 不整合が文書側なら requirements-writer が修正、コード側なら PM → developer 修正ループ | 必須 |
| FR-L3-10 | product-manager は workflow フェーズを **サブタスク化**し各 notes に `担当:` アサインする（親 notes への単一委譲禁止）。`pm_assign_subtasks.py --department development` 可 | 必須 |
| FR-L3-11 | 完了時 PM は `DeptWorkComplete` を orchestrator へ報告し、子タスクを完了マークできる | 必須 |
| FR-L3-12 | `profile=full-ui` 時、PM は UX artifact を notes `## 依存` に転記し、**ux-reviewer**（`ux_implementation`）サブタスクで実装一致 review を経る | 必須 |
| FR-L3-13 | 委譲先ワーカーは着手前に `fetch_task --show-assignee` で `担当:` と自分の slug が一致することを確認する | 必須 |

委譲詳細: [`docs/design/development-pm-assignment.md`](../../../docs/design/development-pm-assignment.md)

### 3.4 L3 — UX チームフェーズ（workflow: `ux-delivery`）

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-L3-U01 | ux-pm は子タスクを読み、**必要タスクをサブタスク化**しメンバーへ `担当:` アサインする（単一 notes 委譲禁止） | 必須 |
| FR-L3-U02 | ux-designer が体験設計書・Design System を作成する | 必須 |
| FR-L3-U03 | ux-reviewer が `ux_spec` レビューを行い `ux_review_passed` を満たす | 必須 |
| FR-L3-U04 | 完了時 ux-pm は `DeptWorkComplete`（`department: ux`）と **artifacts[]** を下流 PM が転記できる形で公開する | 必須 |
| FR-L3-U05 | Web Epic では UX 子を UI 系 development 子より**先**に完了する | 必須 |

詳細: [`docs/design/ux-delivery-io.md`](../../../docs/design/ux-delivery-io.md) · [`docs/design/ux-pm-assignment.md`](../../../docs/design/ux-pm-assignment.md)

### 3.5 L3 — 分析チームフェーズ（workflow: `analysis-delivery`）

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-L3-A01 | analytics-pm は子タスクの background / summary / done_when を読み、分析 delivery を進行管理する | 必須 |
| FR-L3-A02 | analytics-pm はビジネスゴール・KPI・受け入れ基準を定義する | 必須 |
| FR-L3-A03 | data-architect はデータモデルと**契約的 SLA**（更新頻度・遅延許容）を設計する | 必須 |
| FR-L3-A04 | data-engineer / data-steward / data-analyst / data-scientist / ml-engineer は PM から委譲され、各フェーズ完了後 **analysis-reviewer** がレビューする | 必須 |
| FR-L3-A05 | **production_deploy_gate**（品質・セキュリティ・SLA 承認）通過前に ml-engineer は本番デプロイしない | 必須 |
| FR-L3-A06 | データアクセスは RBAC・監査ログの方針に従う（data-architect / data-steward が設計・確認） | 必須 |
| FR-L3-A07 | analytics-pm はリリース判定・ROI 評価・次フェーズ計画を行う | 推奨 |
| FR-L3-A08 | 完了時 analytics-pm は `DeptWorkComplete`（`department: analysis`）を統括グループへ報告する | 必須 |

詳細: [`docs/design/analysis-delivery-io.md`](../../../docs/design/analysis-delivery-io.md)

### 3.6 統括グループ要件

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-X-01 | 新規 `skills/<organization>/<slug>/` は **agent-creater のみ**が作成する | 必須 |
| FR-X-02 | asana-buddy は Handoff 作成・チーム内作業本体を行わない | 必須 |
| FR-X-03 | 親エピックは**全子タスク完了**まで完了としない（orchestrator が集約） | 必須 |
| FR-X-04 | 秘密情報（ASANA_TOKEN 等）はリポジトリにコミットしない | 必須 |
| FR-X-05 | `task-executor` は過渡期として残し、新規は dispatch モデルを推奨する | 必須 |

---

## 4. 非機能要件

| ID | 要件 |
|----|------|
| NFR-01 | workflow / registry は YAML で宣言し、コード変更なしで段階追加を目指す |
| NFR-02 | I/O は JSON Schema で版管理する（Handoff 1.1/1.2、PlanReview、Dispatch、DeptWorkComplete 等） |
| NFR-03 | 既存 `default` v2 E2E を破壊しない（拡張は別 YAML） |
| NFR-04 | Windows / PowerShell 環境で asana-buddy スクリプトが動作する |
| NFR-05 | エージェント運用はプロンプト駆動であり、workflow 段階の**自動実行エンジンは不要**（現行方針） |

---

## 5. エージェント一覧（要件上の役割）

| slug | レイヤー | 要件上の責務 |
|------|----------|--------------|
| workflow-orchestrator | 統括グループ（L1, L2） | intake / bootstrap / dispatch 委譲 / エピック完了集約 |
| planning-pm | L3 | 企画チームハブ（Handoff / review / gate / Asana 投入） |
| issue-story-planner | L3 | Handoff 生成 |
| plan-reviewer | L3 | 企画レビュー |
| asana-buddy | 統括グループ | Asana 作成・読取・完了 |
| task-dispatcher | L2 | チームルーティング |
| product-manager | L3 | 開発チームハブ（profile・委譲・完了） |
| ux-pm | L3 | UX チームハブ（タスク分解・アサイン・artifact 公開） |
| ux-designer / ux-reviewer | L3 | UX チーム委譲 |
| requirements-writer | L3 | 要件定義書・事後詳細仕様 |
| tech-designer | L3 | 技術設計（実装前） |
| developer | L3 | 実装・修正 |
| dev-reviewer | L3 | 要件・設計・コード・mismatch レビュー |
| qa-verifier | L3 | 動作検証 |
| doc-writer / reviewer | L3 | **deprecated**（v1 → requirements-writer / dev-reviewer / qa-verifier） |
| analytics-pm | L3 | 分析チームハブ |
| data-architect / data-engineer / data-steward / data-analyst / data-scientist / ml-engineer | L3 | 分析チーム委譲ロール |
| analysis-reviewer | L3 | 分析チームレビュー・本番デプロイゲート |
| task-executor | L3（レガシー） | 単一ワーカー実行 |
| agent-creater | メタ | スキル雛形生成 |

---

## 6. 受け入れ基準（文書完成時点）

本要件定義書が満たすこと：

1. L1 / L2 / L3 の段階と担当エージェントが一覧できる
2. 子タスク単位配賦と PM ハブの開発・分析フローが追える
3. ゲート（企画 review・チーム内 review・本番デプロイゲート）の位置が明確
4. スコープ外（分析パイプライン実体・実行エンジン）が明示されている

---

## 7. 用語集

| 用語 | 定義 |
|------|------|
| Handoff | planner から asana-buddy への企画 JSON（親 + 子タスク定義） |
| 子タスク | Asana 上のサブタスク 1 件。配賦・チーム内 workflow の単位 |
| department | `development` / `analysis` / `planning` — 配賦先チーム ID |
| DeptWorkComplete | チーム PM（planning-pm / product-manager / analytics-pm）から統括グループへの子タスク完了報告 |
| prompt_snippet | 次スキル起動用のプロンプト文（統括グループ / task-dispatcher が生成） |

---

## 8. 関連文書

- 詳細仕様: [`output/development/specs/agent-composition-spec.md`](../specs/agent-composition-spec.md)
- 組織モデル: [`docs/design/department-model.md`](../../../docs/design/department-model.md) · [`docs/design/org-dispatch-model.md`](../../../docs/design/org-dispatch-model.md)
- チーム内 I/O: [`docs/design/dept-work-io.md`](../../../docs/design/dept-work-io.md)
- 分析チーム I/O: [`docs/design/analysis-delivery-io.md`](../../../docs/design/analysis-delivery-io.md)
