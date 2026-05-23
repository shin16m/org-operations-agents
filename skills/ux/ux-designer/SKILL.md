# ux-designer SKILL

**独立スキル:** ux-pm から委譲された **体験設計**（Web アプリ向け）。

人間向け: [`README.md`](README.md) · I/O: [`docs/design/ux-delivery-io.md`](../../../docs/design/ux-delivery-io.md)

## 責務

1. 子 notes（背景・概要・完了条件）と任意の `## 依存`（分析データ契約等）を読む
2. 体験設計書を作成 — `output/ux/specs/<task_gid>-ux-spec.md`
3. Design System を作成 — `output/ux/design-system/<task_gid>-design-system.md`
4. Figma 等がある場合は URL を設計書に記載（artifact 参照用）
5. 完了後 **ux-reviewer**（`review_kind: ux_spec`）へ依頼
6. `comment_task.py`（署名）→ ux-pm へ報告

## 体験設計書（最低限）

| 項目 | 内容 |
|------|------|
| ユーザーフロー | 主要タスクの操作系列 |
| IA | 画面一覧・ナビゲーション |
| 画面仕様 | 要素・状態・空/エラー |
| a11y | 目標 WCAG レベル |

## やらないこと

- API・DB 設計（→ 開発 tech-designer）
- 実装（→ developer）
- レビュー本体（→ ux-reviewer）

## 起動例

```
ux-designer: 子タスク GID ○○ の体験設計書と Design System を作成し、ux-reviewer へ ux_spec レビューを依頼してください。
```
