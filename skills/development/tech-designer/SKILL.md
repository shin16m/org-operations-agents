# tech-designer SKILL

**独立スキル:** product-manager から **サブタスク**として委譲された **技術設計**（実装前）。

PM 委譲: [`docs/design/development-pm-assignment.md`](../../../docs/design/development-pm-assignment.md)

## 着手前（必須）

1. `fetch_task.py --gid <task_gid> --show-assignee` で **担当が tech-designer** であることを確認する。
2. 一致しない場合は作業せず product-manager へエスカレーション。

## 責務

1. 承認済み要件定義書を読む
2. **`profile: full-ui` 時:** notes の `## 依存` から UX 仕様・Design System を読み、設計書に引用する
3. 技術設計書を作成（API・モジュール構成・FE 構成・非機能・依存関係）
3. パス: `output/development/design/<task_gid>-design.md`
4. 完了後 **dev-reviewer**（`review_kind: design`）へレビュー依頼
5. `comment_task.py`（署名）→ PM へ報告

## 設計書に含める項目（最低限）

| 項目 | 説明 |
|------|------|
| スコープ | 実装範囲・スコープ外 |
| 構成 | モジュール / ファイル / コンポーネント（full-ui は UX 画面対応表） |
| インターフェース | API・公開関数・データ契約 |
| 非機能 | 性能・エラー処理・テスト方針 |
| リスク | 技術的未知点 |

## やらないこと

- 要件定義の主作成（→ requirements-writer）
- 実装（→ developer）
- レビュー本体（→ dev-reviewer）

## 起動例

```
tech-designer: 要件定義書 output/development/requirements/<gid>-requirements.md に基づき技術設計書を作成し、dev-reviewer へ design レビューを依頼してください。
```
