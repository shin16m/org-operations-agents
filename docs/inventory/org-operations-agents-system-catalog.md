# org-operations-agents — システムカタログ

| 版 | 1.2 |
| 日付 | 2026-06-11 |
| Epic GID | 1215611835710268 |
| スコープ | Epic「ドキュメント作成ロール・スキル追加」完了時点 |
| 対象読者 | 依頼者 · 運用担当 · 新規参加者 |
| 正（機械） | `workflows/agent-registry.yaml` · `workflows/organizations.yaml` |

> **参照用の正本は本ファイル（`docs/inventory/`）。**  
> `output/platform/documents/<epic_gid>/system-catalog.md` は実行時コピー（`.gitignore` のため消えることがある）。

---

## 背景

org-ops のエージェント・チーム・workflow の全体像を、レビュー可能な索引としてまとめた文書。registry から全 enabled slug を展開している。

## 概要

和久桶さん（`workflow-orchestrator`）がチャット intake を受け、6 チームの PM へ dispatch し、各 PM がワーカー slug に作業を委譲する。

```mermaid
flowchart LR
  WO[workflow-orchestrator] --> TD[task-dispatcher]
  TD --> PM[各チームPM]
  PM --> W[ワーカー]
  W --> OUT[output/]
```

**エージェント総数:** 33 slug（すべて enabled）

## 詳細

### チーム（department）

| department | ラベル | entry PM | workflow | 成果物ルート |
|------------|--------|----------|----------|--------------|
| planning | 企画チーム | planning-pm | planning-delivery | `output/planning/` |
| development | 開発チーム | product-manager | development-delivery | `output/development/` |
| ux | UX チーム | ux-pm | ux-delivery | `output/ux/` |
| analysis | 分析チーム | analytics-pm | analysis-delivery | `output/analysis/` |
| governance | 組織改善 | governance-pm | governance-delivery | `output/governance/` |
| audit | 監査チーム | audit-pm | audit-delivery | `output/audit/` |

統括（dispatch 対象外）: `skills/platform/` · `output/platform/`

### 統括・platform（4 slug）

| slug | 表示名 | slot | 役割 |
|------|--------|------|------|
| workflow-orchestrator | 統括（和久桶さん） | orchestrate | intake · bootstrap · L2 dispatch |
| task-dispatcher | タスク配賦 | dispatch | department → entry PM へ prompt 生成 |
| asana-buddy | Asana 連携 | execute | Handoff 投入 · comment · complete |
| agent-creater | エージェント生成 | meta | 新規 `skills/<org>/<slug>/` の唯一の生成入口 |

### 企画チーム planning（3 slug）

| slug | 表示名 | slot | 委譲元 |
|------|--------|------|--------|
| planning-pm | 企画 PM | dept_orchestrate | task-dispatcher |
| issue-story-planner | 企画担当 | dept_work | planning-pm |
| plan-reviewer | 企画レビュアー | dept_review | planning-pm |

### 開発チーム development（7 slug）

| slug | 表示名 | slot | 主な成果物 |
|------|--------|------|------------|
| product-manager | 開発 PM | dept_orchestrate | DeptWorkComplete |
| requirements-writer | 要件担当 | dept_work | 要件定義 · 事後仕様 |
| document-author | ドキュメント作成担当 | dept_work | 説明文書 · 企画書 · カタログ |
| tech-designer | 設計担当 | dept_work | 技術設計 |
| developer | 開発担当 | dept_work | コード |
| dev-reviewer | 開発レビュアー | dept_review | Doc/Code/Mismatch review |
| qa-verifier | 動作検証担当 | dept_review | 検証結果 |

### UX チーム ux（4 slug）

| slug | 表示名 | slot |
|------|--------|------|
| ux-pm | UX PM | dept_orchestrate |
| ux-designer | UX 設計担当 | dept_work |
| design-system-owner | Design System 担当 | dept_work |
| ux-reviewer | UX レビュアー | dept_review |

### 分析チーム analysis（9 slug）

| slug | 表示名 | slot |
|------|--------|------|
| analytics-pm | 分析 PM | dept_orchestrate |
| analytics-requirements-writer | 分析要件担当 | dept_work |
| data-architect | データアーキテクト | dept_work |
| data-engineer | データエンジニア | dept_work |
| data-steward | データスチュワード | dept_work |
| data-analyst | データアナリスト | dept_work |
| data-scientist | データサイエンティスト | dept_work |
| ml-engineer | ML エンジニア | dept_work |
| analysis-reviewer | 分析レビュアー | dept_review |

### 組織改善 governance（3 slug）

| slug | 表示名 | slot |
|------|--------|------|
| governance-pm | 組織改善 PM | dept_orchestrate |
| ssot-implementer | SSOT 実装担当 | dept_work |
| governance-reviewer | 組織改善レビュアー | dept_review |

### 監査 audit（3 slug）

| slug | 表示名 | slot |
|------|--------|------|
| audit-pm | 監査 PM | dept_orchestrate |
| consistency-auditor | 整合性監査担当 | dept_work |
| audit-reviewer | 監査レビュアー | dept_review |

### workflow 一覧

| workflow_id | 版 | 用途 | entry_agent |
|-------------|-----|------|-------------|
| default | v6 | チャット intake → bootstrap → 企画 dispatch | workflow-orchestrator |
| with-dispatch | v2 | 上記 + execution 系子の L2 dispatch ループ | workflow-orchestrator |
| planning-delivery | — | 企画 L3 | planning-pm |
| development-delivery | v3 | 開発 L3 | product-manager |
| ux-delivery | v2 | UX L3 | ux-pm |
| analysis-delivery | v2 | 分析 L3 | analytics-pm |
| governance-delivery | — | 組織改善 L3 | governance-pm |
| audit-delivery | — | 監査 L3 | audit-pm |

### 和久桶さん intake モード

| モード | いつ使う | bootstrap |
|--------|----------|-----------|
| natural_language | 課題受付（既定） | あり |
| task_creation_request | タスク化相談 | あり |
| epic_input | 既存 Epic 遂行 | 省略 |
| document_request | 単发文書化 | 省略 |

### 本 Epic で追加・変更したもの

| 種別 | 内容 |
|------|------|
| 新 slug | `document-author` |
| UX テンプレ | `output/ux/document-author/`（4 点 · **git 管理**） |
| orchestrator | §A-5 document_request · §D epic_documentation |
| 設計 doc | `output/governance/document-author-design.md` |

## まとめ

- **レビュー・参照:** 本ファイル（`docs/inventory/org-operations-agents-system-catalog.md`）
- **更新:** registry 変更後に `document-author`（mode=catalog）で再生成し、本ファイルへ反映
- **関連:** [`skill-persona-matrix.md`](skill-persona-matrix.md) · [`skills-inventory.md`](skills-inventory.md)
