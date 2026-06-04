# development — 開発チーム

子タスク 1 件あたり `development-delivery` workflow **v3**。PM がハブ。

| slug | 役割 |
|------|------|
| product-manager | 進行・profile・**サブタスク分解**・委譲・完了 |
| requirements-writer | 要件定義・事後詳細仕様 |
| tech-designer | 技術設計（実装前） |
| developer | 実装 |
| dev-reviewer | 文書・コード・整合レビュー |
| qa-verifier | 動作検証 |

**full-ui 時:** UX チーム `ux-reviewer` が実装一致 review（[`ux-delivery-io.md`](../../docs/design/ux-delivery-io.md)）

## delivery profile

| profile | 用途 |
|---------|------|
| `full` | API / 非 UI |
| `full-ui` | Web 画面（UX 依存必須） |
| `lite` | 小変更・非 UI |
| `doc-only` | org-meta / 仕様のみ |

assign plan 例: [`examples/assign-plan.full-ui-v1.json`](examples/assign-plan.full-ui-v1.json) · [`assign-plan.lite-v1.json`](examples/assign-plan.lite-v1.json) · [`assign-plan.doc-only-v1.json`](examples/assign-plan.doc-only-v1.json) · [`assign-plan.dev-workflow-review-v1.json`](examples/assign-plan.dev-workflow-review-v1.json)

成果物: [`output/development/`](../../output/development/)

I/O: [`docs/design/development-delivery-io.md`](../../docs/design/development-delivery-io.md) · PM 委譲: [`docs/design/development-pm-assignment.md`](../../docs/design/development-pm-assignment.md)（**profile 選定ガイド** §）
