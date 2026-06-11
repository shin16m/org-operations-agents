# document-author SKILL

**依頼者向け:** 和久桶さんに **「文書化して」** + URL または本文 — それだけで可（[`document_request`](../../../docs/design/wakuoke-intake-modes.md#d-文書化依頼document_request)）。

**独立スキル:** workflow-orchestrator または product-manager から委譲された **読み手向け説明文書**の作成。

人間向け: [`README.md`](README.md) · persona: [`personas/document_author.md`](personas/document_author.md) · 設計: [`output/governance/document-author-design.md`](../../../output/governance/document-author-design.md)

## 着手前（必須）

1. `fetch_task.py --gid <task_gid> --show-assignee` で **担当が document-author** であることを確認（単発依頼時は orchestrator セッション内で slug として起動可）。
2. 文書種別を確定: `general` | `planning` | `catalog` | `report`

## テンプレ（必須参照）

| 種別 | テンプレ |
|------|----------|
| 汎用説明・レポート | [`output/ux/document-author/template-general-doc.md`](../../../output/ux/document-author/template-general-doc.md) |
| 依頼者向け企画書 | [`output/ux/document-author/template-planning-doc.md`](../../../output/ux/document-author/template-planning-doc.md) |
| システムカタログ | [`output/ux/document-author/template-system-catalog.md`](../../../output/ux/document-author/template-system-catalog.md) |
| 図表 | [`output/ux/document-author/diagram-guide.md`](../../../output/ux/document-author/diagram-guide.md) |

## 文書種別（mode）

| mode | 入力 | 成果物パス |
|------|------|------------|
| `general` | チャットインプット · notes | `output/development/documents/<task_gid>/` |
| `planning` | Handoff JSON · PlanReviewResult | `output/platform/documents/<epic_gid>/planning-doc.md` |
| `catalog` | `agent-registry.yaml` · `organizations.yaml` | **`docs/inventory/org-operations-agents-system-catalog.md`**（正本）· 任意で `output/platform/documents/<epic_gid>/` にコピー |
| `report` | 分析メモ · 調査結果 | `output/development/documents/<task_gid>/report.md` |

## 責務

1. インプットを読み、該当テンプレに沿って MD を生成する
2. Mermaid は diagram-guide 準拠（15 ノード以下 · style 禁止）
3. 完了前に **comment_task.py**（`--agent document-author`）→ 依頼元 PM / orchestrator へ報告
4. Asana 使用時: 成果物 MD を `attach_task_files.py` で添付（任意）

## 起動経路

| 経路 | 起動者 | 備考 |
|------|--------|------|
| `document_request` | workflow-orchestrator | **「文書化して」** — 和久桶が同一セッションで本スキルとして執筆（丸投げ禁止） |
| `epic_documentation` | workflow-orchestrator | planning 後 · Epic 締め前 |
| development 子 | product-manager | doc-only profile |

起動例（単発）:

```
document-author として次を文書化してください。

〈インプット〉…
〈文書種別〉general
〈出力先〉output/development/documents/adhoc-001/
```

## やらないこと

- 要件定義・AC 表（→ requirements-writer）
- registry / workflow の変更（→ ssot-implementer / developer）
- レビュー判定（→ dev-reviewer / ux-reviewer）

## Asana

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py `
  --gid <GID> --agent document-author --skill skills/development/document-author/SKILL.md `
  --summary "説明文書作成完了" --body "成果物: output/..." -y
```
