# 要件定義書 — エージェント構成とワークフロー

| 項目 | 内容 |
|------|------|
| 文書種別 | 要件定義書（requirements-doc） |
| 作成者ロール | product-manager |
| 対象 | agent-create-supporter リポジトリ全体のマルチエージェント構成 |
| 参照 workflow | `default` v2 · `with-dispatch` · `development-delivery` · `analysis-delivery` |
| 版 | 1.1 |
| 日付 | 2026-05-23 |

---

## 1. 背景と目的

### 1.1 背景

本リポジトリは、Cursor / Copilot 上で動作する**スキルベースのエージェント群**を Git 共有し、次の流れを実現する。

1. 利用者が自然言語で課題を提示する
2. 企画（ストーリー・タスク案）→ レビュー → Asana タスク化まで行う
3. Asana 上の**子タスクごと**に、適切な「課」へ配賦し、開発・文書・レビューを進める

従来は `task-executor` が子タスクを単独で処理していた。組織配賦コミット（`7f91132`）以降、**開発課は PM ハブ + 専門ロール**へ移行する。

### 1.2 目的

- 利用者が**スキル名を覚えず**、オーケストレーターに話しかけるだけで企画〜実行に進める
- 企画品質を `plan-reviewer` で担保してから Asana 投入する
- **子タスク 1 件 = 配賦 1 回 = 課内ワークフロー 1 本**で、開発・分析が混在するエピックを扱える
- 新規エージェント追加時に workflow / registry を拡張し、オーケストレーターを肥大化させない

### 1.3 スコープ

| 含む | 含まない |
|------|----------|
| 全業務スキル・メタスキルの役割と連携 | Asana ワークスペースの人事・アサイン実務 |
| L1 企画 / L2 配賦 / L3 課内の責務 | workflow YAML の実行エンジン実装 |
| Handoff・レビュー・配賦・完了報告の I/O | 分析パイプライン・モデルの**製品コード**（別リポジトリ） |
| 過渡期の `task-executor` | 外部 SaaS（Notion 等）連携 |

---

## 2. ステークホルダーと利用者像

| 役割 | ニーズ |
|------|--------|
| **利用者（依頼者）** | 自然言語のみで依頼。企画書（Asana）と実行結果を得たい |
| **オーケストレーター** | 入口・ゲート・配賦委譲・エピック完了の集約 |
| **企画課（planner / reviewer）** | エピック単位の Handoff と品質レビュー |
| **タスクディスパッチャー** | 子タスクを課へルーティング |
| **開発課 PM** | 子 1 件のライフサイクル管理 |
| **開発課メンバー** | 文書・実装・レビュー・検証 |
| **asana 管理者** | タスク CRUD・読取・完了マーク（横断） |
| **agent-creater** | 新規スキル雛形の唯一の生成入口 |

---

## 3. 機能要件

### 3.1 L1 — 企画フェーズ（workflow: `default` v2）

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-L1-01 | 利用者は **workflow-orchestrator（intake）** を唯一の入口とする | 必須 |
| FR-L1-02 | orchestrator は生課題を受け、**issue-story-planner** 用 `prompt_snippet` を返す | 必須 |
| FR-L1-03 | planner は **AsanaBuddyHandoff**（v1.1 または v1.2）を 1 件出力する | 必須 |
| FR-L1-04 | **plan-reviewer** によるレビューは省略不可（`review_required: true`） | 必須 |
| FR-L1-05 | reviewer は `PlanReviewResult`（`passed` / `passed_with_notes` / `failed`）を返す | 必須 |
| FR-L1-06 | orchestrator（gate）は review 結果を確認し、execute 可否を判定する | 必須 |
| FR-L1-07 | **asana-buddy** は承認済み Handoff から親エピック + 子タスクを作成する | 必須 |
| FR-L1-08 | CLI 投入時は `--require-review-result` で review ゲートを強制できる | 推奨 |
| FR-L1-09 | v1.2 では実行系子タスクに `department` を付与できる | 推奨 |

**ゲート**

- `review_passed`: 未達時は gate / execute / dispatch 不可
- `handoff_approved`: 人間が gate 経由で execute を許可

### 3.2 L2 — 配賦フェーズ（workflow: `with-dispatch`）

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-L2-01 | execute 完了後、**子タスク 1 件単位**で実行依頼を受け付ける | 必須 |
| FR-L2-02 | orchestrator は未完了子を列挙し、**task-dispatcher** へ委譲する | 必須 |
| FR-L2-03 | dispatcher は `department` に基づき課 workflow の **entry_agent** へルーティングする | 必須 |
| FR-L2-04 | ルーティング表は `workflows/organizations.yaml` に宣言的に定義する | 必須 |
| FR-L2-05 | `department=development` のとき **product-manager** を起動する | 必須 |
| FR-L2-06 | `department=analysis` のとき **analytics-pm** を起動する | 必須 |
| FR-L2-07 | `department` 未設定時は Handoff の `pillar` または Asana notes の `課:` 行から推定する | 推奨 |

### 3.3 L3 — 開発課フェーズ（workflow: `development-delivery`）

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-L3-01 | PM は子タスクの background / summary / done_when を読み、進行を管理する | 必須 |
| FR-L3-02 | **doc-writer** が要件定義書を作成し、**reviewer** がレビューする | 必須 |
| FR-L3-03 | 要件定義 OK 後、PM は **developer** に開発を依頼する | 必須 |
| FR-L3-04 | developer はコードレビュー・動作検証を経て PM に開発完了を報告する | 必須 |
| FR-L3-05 | PM は **doc-writer** に詳細仕様書作成を依頼する | 必須 |
| FR-L3-06 | reviewer は要件定義書と詳細仕様の**整合レビュー**を行う | 必須 |
| FR-L3-07 | 不整合が文書側なら doc-writer が修正、コード側なら PM → developer 修正ループ | 必須 |
| FR-L3-08 | 完了時 PM は `DeptWorkComplete` を orchestrator へ報告し、子タスクを完了マークできる | 必須 |

### 3.4 L3 — 分析課フェーズ（workflow: `analysis-delivery`）

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-L3-A01 | analytics-pm は子タスクの background / summary / done_when を読み、分析 delivery を進行管理する | 必須 |
| FR-L3-A02 | analytics-pm はビジネスゴール・KPI・受け入れ基準を定義する | 必須 |
| FR-L3-A03 | data-architect はデータモデルと**契約的 SLA**（更新頻度・遅延許容）を設計する | 必須 |
| FR-L3-A04 | data-engineer / data-steward / data-analyst / data-scientist / ml-engineer は PM から委譲され、各フェーズ完了後 **analysis-reviewer** がレビューする | 必須 |
| FR-L3-A05 | **production_deploy_gate**（品質・セキュリティ・SLA 承認）通過前に ml-engineer は本番デプロイしない | 必須 |
| FR-L3-A06 | データアクセスは RBAC・監査ログの方針に従う（data-architect / data-steward が設計・確認） | 必須 |
| FR-L3-A07 | analytics-pm はリリース判定・ROI 評価・次フェーズ計画を行う | 推奨 |
| FR-L3-A08 | 完了時 analytics-pm は `DeptWorkComplete`（`department: analysis`）を orchestrator へ報告する | 必須 |

詳細: [`docs/design/analysis-delivery-io.md`](../design/analysis-delivery-io.md)

### 3.5 横断要件

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-X-01 | 新規 `skills/<slug>/` は **agent-creater のみ**が作成する | 必須 |
| FR-X-02 | asana-buddy は Handoff 作成・課内作業本体を行わない | 必須 |
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
| workflow-orchestrator | L1, L2 | intake / gate / dispatch 委譲 / エピック完了集約 |
| issue-story-planner | L1 | Handoff 生成 |
| plan-reviewer | L1 | 企画レビュー |
| asana-buddy | 横断 | Asana 作成・読取・完了 |
| task-dispatcher | L2 | 課ルーティング |
| product-manager | L3 | 開発課ハブ |
| analytics-pm | L3 | 分析課ハブ |
| doc-writer | L3 | 要件定義書・詳細仕様書 |
| developer | L3 | 実装・修正 |
| reviewer | L3 | 開発課レビュー・検証 |
| data-architect / data-engineer / data-steward / data-analyst / data-scientist / ml-engineer | L3 | 分析課委譲ロール |
| analysis-reviewer | L3 | 分析課レビュー・本番デプロイゲート |
| task-executor | L3（レガシー） | 単一ワーカー実行 |
| agent-creater | メタ | スキル雛形生成 |

---

## 6. 受け入れ基準（文書完成時点）

本要件定義書が満たすこと：

1. L1 / L2 / L3 の段階と担当エージェントが一覧できる
2. 子タスク単位配賦と PM ハブの開発・分析フローが追える
3. ゲート（企画 review・課内 review・本番デプロイゲート）の位置が明確
4. スコープ外（分析パイプライン実体・実行エンジン）が明示されている

---

## 7. 用語集

| 用語 | 定義 |
|------|------|
| Handoff | planner から asana-buddy への企画 JSON（親 + 子タスク定義） |
| 子タスク | Asana 上のサブタスク 1 件。配賦・課内 workflow の単位 |
| department | `development` / `analysis` / `planning` — 配賦先の課 ID |
| DeptWorkComplete | 課 PM（product-manager / analytics-pm）から orchestrator への子タスク完了報告 |
| prompt_snippet | 次スキル起動用のプロンプト文（orchestrator / dispatcher が生成） |

---

## 8. 関連文書

- 詳細仕様: [`docs/specs/agent-composition-spec.md`](../specs/agent-composition-spec.md)
- 組織モデル: [`docs/design/org-dispatch-model.md`](../design/org-dispatch-model.md)
- 課内 I/O: [`docs/design/dept-work-io.md`](../design/dept-work-io.md)
- 分析課 I/O: [`docs/design/analysis-delivery-io.md`](../design/analysis-delivery-io.md)
