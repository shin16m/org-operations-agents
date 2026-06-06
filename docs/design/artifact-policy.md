# 成果物ポリシー — テンプレ vs 実行時

| 版 | 1.1 |
| 日付 | 2026-06-07 |
| 適用 | org-operations-agents テンプレートリポジトリ |

## 原則

1. **本リポジトリは汎用組織テンプレート** — スキル・workflow・契約 doc をバージョン管理する。**特定プロダクト・ドメイン向けのルールや assign plan は載せない。**
2. **エピック成果物は管理外** — 要件・コード・CSV・モデル・レビュー JSON 等は `output/` に書き、**git に載せない**。
3. **ローカルカスタム** — アプリ開発やドメイン固有の運用変更（assign plan 実行版・Handoff・ダッシュボード実装等）は **fork 先の `output/` / `work/` のみ**で行う。汎用テンプレへの逆流（コミット）はしない。
4. **パス convention は SSOT** — `organizations.yaml` の `output_root` と各 `*-delivery-io.md` が実行時の書き込み先を定義する。
5. **チーム間共有** — artifact URI は Asana notes の `## 依存（読み取り専用）` 経由（[`department-model.md`](department-model.md)）。

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
