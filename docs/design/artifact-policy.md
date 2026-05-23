# 成果物ポリシー — テンプレ vs 実行時

| 版 | 1.0 |
| 日付 | 2026-05-23 |
| 適用 | org-operations-agents テンプレートリポジトリ |

## 原則

1. **本リポジトリは組織テンプレート** — スキル・workflow・契約 doc をバージョン管理する。
2. **エピック成果物は管理外** — 要件・コード・CSV・モデル・レビュー JSON 等は `output/` に書き、**git に載せない**。
3. **パス convention は SSOT** — `organizations.yaml` の `output_root` と各 `*-delivery-io.md` が実行時の書き込み先を定義する。
4. **チーム間共有** — artifact URI は Asana notes の `## 依存（読み取り専用）` 経由（[`department-model.md`](department-model.md)）。

## git 管理の境界

| 種別 | パス | git |
|------|------|-----|
| スキル・workflow | `skills/`, `workflows/`, `docs/design/` | ○ |
| assign plan 雛形 | `skills/*/examples/assign-plan*.json` | ○ |
| 検証 fixture | `docs/verification/fixtures/` | ○ |
| PM assign plan（実行） | `work/assign-plans/*.json` | × |
| チーム成果物 | `output/**`（README / `.gitkeep` 除く） | × |
| dryrun スタブ | `output/dryrun/**` | × |

## フォルダテンプレ

`output/` と `work/assign-plans/` は **`.gitkeep` のみ**リポジトリに含め、fork 先でそのまま使えるようにする。

## 永続化が必要な成果物

- **プロジェクト別 Git リポジトリ**（製品アプリ・分析パイプライン等）
- または外部ストレージ + Asana notes で URI 参照

製品ソースを本テンプレ repo に置かない（[`README.md`](../../README.md) スコープ）。
