# チーム間 artifact bridge — 価値が継ぎ目で落ちないために

| 版 | 1.1 |
| 日付 | 2026-06-06 |
| 焦点 | UX → 開発 · **分析 → 開発** |

## 問題

チーム間の公式 I/O は Asana notes のみだが、**markdown パス参照だけ**では「これいいな」と感じる UI の意図が開発まで伝わらない。価値最大化には **実デザイン資産**を契約に含める。

## 原則（既存の拡張）

[`department-model.md`](department-model.md) の成果物共有を維持しつつ、依存表の **参照列**を格上げする。

| 層 | 旧（v1） | 新（v2 推奨） |
|----|----------|---------------|
| UX 仕様 | `output/ux/specs/<gid>-ux-spec.md` | 同上 **+ Figma ファイル URL / node-id** |
| Design System | `output/ux/design-system/<gid>-design-system.md` | 同上 **+ Figma 変数・コンポーネント** |
| 開発 consume | markdown 読み取り | markdown + Figma + **Code Connect**（任意） |

**禁止は変わらない:** 他チーム `output/` の無契約探索 · 他チーム成果物の編集。

## UX → 開発の標準 `## 依存（読み取り専用）`

product-manager が full-ui 子 intake 前に追記する。

```markdown
## 依存（読み取り専用）

| 種別 | 参照 | バージョン | 提供チーム |
|------|------|------------|------------|
| UX 仕様 | `output/ux/specs/<ux_child_gid>-ux-spec.md` | v1.0 | ux |
| Figma UI | https://www.figma.com/design/<file>?node-id=<id> | v1.0 | ux |
| Design System | `output/ux/design-system/<ux_child_gid>-design-system.md` | v1.0 | ux |
| Figma DS | https://www.figma.com/design/<file>?node-id=<ds-id> | v1.0 | ux |
| Code Connect | `output/ux/code-connect/<ux_child_gid>/`（任意） | v1.0 | ux |

**利用条件:** 読み取り・呼び出しのみ。ビジュアル変更は UX チームの子タスクで依頼する。
```

## 各チームの責務

### UX チーム（提供側）

| 順 | 担当 | 操作 |
|----|------|------|
| 1 | ux-pm / ワーカー | Figma で実 UI・DS を作成（[`ux-delivery-io.md`](ux-delivery-io.md) v2） |
| 2 | ux-pm | `DeptWorkComplete.artifacts[]` に md パス **と Figma URL** を含める |
| 3 | design-system-owner（任意） | Code Connect テンプレを `output/ux/code-connect/<gid>/` に出力 |

### 開発チーム（消費側）

| 順 | 担当 | 操作 |
|----|------|------|
| 1 | product-manager | UX 子完了後、上表を development 子 notes に転記 → **`pm_intake_gate.py` exit 0** |
| 2 | tech-designer | 設計書に画面対応表 + Figma node 参照を記載 |
| 3 | developer | Figma / Code Connect を read-only で実装 |
| 4 | ux-reviewer | `ux_implementation` でビジュアル一致を検証 |

**dryrun 記録:** [`ux-to-dev-full-ui-dryrun.md`](../verification/cross-team/ux-to-dev-full-ui-dryrun.md) · Handoff 例: [`handoff.ux-web-app.json`](../../skills/planning/issue-story-planner/examples/handoff.ux-web-app.json)

## 分析 → 開発

分析チーム（`profile: model-serve` / `full`）完了後、開発がモデル・API・カタログを consume する。

### 標準 `## 依存（読み取り専用）`

product-manager が development 子 intake 前に追記する（`profile: full` で API 連携時など）。

```markdown
## 依存（読み取り専用）

| 種別 | 参照 | バージョン | 提供チーム |
|------|------|------------|------------|
| データカタログ | `output/analysis/catalog/<analysis_child_gid>.md` | v1.0 | analysis |
| モデル | `output/analysis/models/<analysis_child_gid>/` | v1.0 | analysis |
| 推論 API | https://api.example.com/v1/predict（または内部 URL） | v1.0 | analysis |
| SLA | 日次更新・遅延最大 2h（data-architect 設計書参照） | — | analysis |

**利用条件:** 読み取り・呼び出しのみ。契約変更は分析チームの子タスクで依頼する。
```

### 責務

| 側 | 担当 | 操作 |
|----|------|------|
| 提供 | analytics-pm | `DeptWorkComplete.artifacts[]` にパス · API URL · バージョン · SLA 参照 |
| 消費 | product-manager | 上表を development 子 notes に転記してから着手 |
| 消費 | tech-designer / developer | 依存表どおり read-only。不足は analytics-pm へ差し戻し |

詳細: [`analysis-delivery-io.md`](analysis-delivery-io.md) · [`analytics-pm-assignment.md`](analytics-pm-assignment.md)

**dryrun 記録:** [`analysis-to-dev-dryrun.md`](../verification/cross-team/analysis-to-dev-dryrun.md) · Handoff 例: [`handoff.analysis-model-serve.json`](../../skills/planning/issue-story-planner/examples/handoff.analysis-model-serve.json)

---

## Figma MCP の使い方（運用メモ）

Cursor 環境では Figma MCP スキル（`figma-generate-design` / `figma-generate-library`）を **ux-designer / design-system-owner** が使用する。

1. `figma-generate-design` — 画面モック・複数案（`profile: flagship`）
2. `figma-generate-library` — トークン・コンポーネント
3. 完了時に Figma URL を ux-spec / DeptWorkComplete に記載

## 関連

- UX delivery v2: [`ux-delivery-io.md`](ux-delivery-io.md)
- 開発 full-ui: [`development-delivery-io.md`](development-delivery-io.md)
- 強みの型: [`delivery-strength-pattern.md`](delivery-strength-pattern.md)
