# スキル棚卸し（agent-create-supporter）

更新: エピック「マルチエージェント基盤」タスク 1 成果物。設計の単一参照: [`skills/issue-story-planner/examples/handoff.agent-workflow-orchestration.json`](../../skills/issue-story-planner/examples/handoff.agent-workflow-orchestration.json)。

## 新規エージェント作成の入口

**`agent-creater` のみ**が `skills/<slug>/` の設計・雛形を生成する。他スキル・オーケストレーターは新規フォルダを作らない。

## スキル一覧

| slug | 種別 | スロット | 状態 | I/O 概要 | サブタスク対応 |
|------|------|----------|------|----------|----------------|
| `agent-creater` | メタ | — | 実装済 | 要件 → README/SKILL/personas 雛形 | 5, 6, 7 の生成元・9 |
| `issue-story-planner` | 業務 | `plan` | 実装済 | 課題 → AsanaBuddyHandoff v1.1 | 2, 5, 8, 9 |
| `asana-buddy` | 業務 | `execute` | 実装済 | Handoff v1.1 → Asana API | 2, 5, 8, 9, 11 |
| `plan-reviewer` | 業務 | `review` | **本エピックで追加** | Handoff v1.1 → 改訂 Handoff / レビュー結果 | 4, 6, 9 |
| `workflow-orchestrator` | 業務 | `orchestrate` | **本エピックで追加** | workflow + registry 参照 → 次スキル案内 | 2, 3, 7, 8, 9 |

## ギャップ（エピック前）

| 項目 | 現状 | 対応タスク |
|------|------|------------|
| プラン品質ゲート | なし | 4, 6 |
| オーケストレーション | 手動でスキル連携 | 2, 3, 7 |
| 宣言的 workflow / registry | なし | 3 |
| ルート README / CONTRIBUTING | なし | 10 |
| E2E 手順の一本化 | 各 SKILL に分散 | 8, 11 |
| SKILL への委任・パイプライン明記 | Handoff のみ | 5（最小）, 9（本格） |

## SKILL 未反映項目（タスク 5 / 9 で解消）

| SKILL | 未反映（タスク 1 時点） | 対応 |
|-------|-------------------------|------|
| `agent-creater` | 唯一の作成入口・エコシステム図 | 5 最小 → 9 本格 |
| `issue-story-planner` | plan→review→asana、agent-creater 委任 | 5 → 9 |
| `asana-buddy` | レビュー済み Handoff 推奨、パイプライン | 5 → 9 |

## レガシー

| パス | 扱い |
|------|------|
| `skills/agent-creater/agents/asana-buddy/` | **廃止**。正は `skills/asana-buddy/`。削除は別 PR 可。スクリプトは新パスの `.env` をフォールバック参照。 |

## Handoff 例

| ファイル | 用途 |
|----------|------|
| `handoff.example.json` | 汎用例 |
| `handoff.agent-workflow-orchestration.json` | 本エピック・基盤構築の設計書兼 Handoff |
