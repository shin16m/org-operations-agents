# org-operations-agents — システムカタログ

| 版 | 1.0 |
| 日付 | YYYY-MM-DD |
| スコープ | 〈例: 本 Epic 完了時点 / 全体〉 |
| 対象読者 | 依頼者 · 運用担当 · 新規参加者 |

---

## 背景

**このカタログの目的。** registry・workflow・skills の全体像を読者が辿れる索引とする。

## 概要

org-ops は **宣言的 workflow + agent-registry** でエージェント役割を定義し、和久桶さん（workflow-orchestrator）が intake → 各チーム PM へ dispatch する。

```mermaid
flowchart LR
  WO[workflow-orchestrator] --> PM[各チーム PM]
  PM --> W[ワーカー slug]
  W --> OUT[output/ 成果物]
```

## 詳細

### チーム（department）一覧

| department | ラベル | entry PM | workflow | 成果物ルート |
|------------|--------|----------|----------|--------------|
| planning | 企画チーム | planning-pm | planning-delivery | `output/planning/` |
| development | 開発チーム | product-manager | development-delivery | `output/development/` |
| ux | UX チーム | ux-pm | ux-delivery | `output/ux/` |
| analysis | 分析チーム | analytics-pm | analysis-delivery | `output/analysis/` |
| governance | 組織改善 | governance-pm | governance-delivery | `output/governance/` |
| audit | 監査チーム | audit-pm | audit-delivery | `output/audit/` |

※ 実データは `workflows/organizations.yaml` から生成時に同期する。

### 主要エージェント（slug）抜粋

| slug | 表示名 | slot | skill_path |
|------|--------|------|------------|
| workflow-orchestrator | 和久桶さん | orchestrate | `skills/platform/workflow-orchestrator` |
| document-author | ドキュメント作成担当 | dept_work | `skills/development/document-author` |
| … | … | … | … |

※ 全量は `workflows/agent-registry.yaml` を機械抽出して表を埋める。

### workflow 対応

| workflow_id | 説明 | entry_agent |
|-------------|------|-------------|
| default | L1 intake / bootstrap / dispatch | workflow-orchestrator |
| planning-delivery | 企画 L3 | planning-pm |
| ux-delivery | UX L3 | ux-pm |
| … | … | … |

### 入口（和久桶さん intake）

| モード | いつ使う |
|--------|----------|
| natural_language | 課題受付（既定） |
| task_creation_request | タスク化相談 |
| epic_input | 既存 Epic 遂行 |
| document_request | 単发文書化 |

## まとめ

- **カタログの更新タイミング:** Epic 完了前 · registry 変更後
- **正（機械）:** `workflows/agent-registry.yaml` · `workflows/organizations.yaml`
- **人間向け索引（レビュー用・git 管理）:** `docs/inventory/org-operations-agents-system-catalog.md`
- **実行時コピー（任意）:** `output/platform/documents/<epic_gid>/system-catalog.md`（`.gitignore` · 消えることがある）

---

## 生成時チェックリスト

- [ ] registry から slug 一覧を抽出したか
- [ ] disabled slug を除外したか
- [ ] 図は 1〜2 枚に抑えたか（詳細は表へ）
