# design-system-owner SKILL

**独立スキル:** ux-pm から **サブタスク**として委譲された **Design System**（Figma 変数・コンポーネント + 文書 SSOT）。

人間向け: [`README.md`](README.md) · I/O: [`docs/design/ux-delivery-io.md`](../../../docs/design/ux-delivery-io.md) · PM 委譲: [`docs/design/ux-pm-assignment.md`](../../../docs/design/ux-pm-assignment.md)

## 着手前（必須）

1. `fetch_task.py --gid <task_gid> --show-assignee` で **担当が design-system-owner** であることを確認する。
2. 一致しない場合は作業せず ux-pm へエスカレーション。
3. 同一 Epic で ux-designer の Figma UI が存在する場合は、**視覚方向に整合**させる（未完了なら ux-pm へエスカレーション）。

## 責務

1. サブタスク notes と ux-designer の Figma URL（依存節または前フェーズ成果）を読む
2. **Figma** で Design System を構築（変数・タイポ・Spacing・Color・コンポーネント）
   - Cursor 環境: `figma-generate-library` スキルを使用
3.  companion 文書を作成:
   - `output/ux/design-system/<task_gid>-design-system.md`（トークン表・コンポーネント一覧・利用ルール）
4. 任意: Code Connect テンプレを `output/ux/code-connect/<parent_gid>/` に出力
5. 完了前に **comment_task.py**（署名）→ ux-pm へ報告

**profile: lite** では本ロールは通常スキップ（既存 DS 参照のみ）。

## Design System 文書（最低限）

| 項目 | 内容 |
|------|------|
| Figma URL | DS ファイル / ライブラリへのリンク |
| トークン | Color · Typography · Spacing · Radius · Shadow |
| コンポーネント | Button · Input · Card 等の variant 定義 |
| 利用ルール | 開発が迷わない Do / Don't |

## Asana

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\comment_task.py `
  --gid <GID> --agent design-system-owner --skill skills/ux/design-system-owner/SKILL.md --summary "..." --body "..." -y
```

## やらないこと

- 画面フロー・IA の主設計（→ ux-designer）
- 実装（→ developer）
- レビュー本体（→ ux-reviewer）

## 起動例

```
あなたは design-system-owner スキルです。Asana サブタスク GID ○○ の notes を読み、
Figma で Design System を構築し design-system.md を保存してから comment_task.py を実行してください。
```
