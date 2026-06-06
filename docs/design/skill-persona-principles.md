# スキルとペルソナの持ち方 — 設計原則

| 版 | 1.0 |
| 日付 | 2026-06-06 |
| 関連 | [`delivery-strength-pattern.md`](delivery-strength-pattern.md) · [`department-model.md`](department-model.md) |

## 目的

エージェントの **運用契約（SKILL）** と **価値観・振る舞い（persona）** を分離し、チーム特性に応じた粒度でスキルを持つ。全チームを同一ロール数に揃えることは目標としない。

## 二層モデル

| 層 | 置き場 | 書くこと | 書かないこと |
|----|--------|----------|--------------|
| **SKILL.md** | `skills/<team>/<slug>/` | I/O 契約 · 着手前チェック · 成果物パス · Asana 手順 · やらないこと | 長い人格劇 · 重複する例文 |
| **persona** | `personas/<slug>.md` | ミッション一文 · **志向**（品質バー・判断軸）· 協調関係 | CLI · パス · ゲート名（→ SKILL へ） |

**正典:** persona は **Markdown のみ**（新規 `.json` は作らない）。

## 粒度の方針（チーム別）

| チーム | ロール数の考え方 | 備考 |
|--------|------------------|------|
| **開発** | 多め（PM + 要件 + 設計 + 実装 + 2 種 review） | v3 が参照実装 |
| **UX** | 探索が要る分だけ分割 | designer / DS owner / reviewer。**researcher は v2 では designer が IA・フロー探索を兼担**（下記） |
| **分析** | パイプライン段階ごと + requirements-writer | profile でフェーズ省略 |
| **企画** | 小（PM + planner + reviewer） | Handoff 特化 |
| **監査** | 最小（PM + auditor + reviewer） | 変更頻度低 |
| **組織改善** | 最小（PM + implementer + reviewer） | org-meta 特化 |
| **統括** | 配線のみ | dispatch 対象外 |

## ux-researcher について（現時点の判断）

| 項目 | 内容 |
|------|------|
| **v2 の扱い** | **専ロールは追加しない**。`profile: flagship` 時の IA・ユーザーフロー探索は **ux-designer** が担当 |
| **将来** | 探索を厚くし designer がビジュアルに専念する必要が出たら `ux-researcher` を agent-creater 経由で追加 |
| **SKILL 上の明示** | [`ux-designer/SKILL.md`](../../skills/ux/ux-designer/SKILL.md) · flagship は複数案 + IA |

## persona テンプレ（推奨）

```markdown
# {表示名}

{ミッションを 1〜2 文。誰のために何を届けるか}

**志向:** {品質バー・判断軸を 3〜5 語句}

**協調:** {隣接ロールとの関係を 1 行、任意}
```

**志向の例**

| ロール | 志向の例 |
|--------|----------|
| ux-designer | 凡庸回避 · 複数案 · 次アクションの明確さ |
| developer | 仕様忠実 · 最小差分 · 読みやすいコード |
| data-architect | SLA 明文化 · 下流が迷わない契約 |
| consistency-auditor | 機械的整合 · 推測しない |

**PM ペルソナ:** 進行・分解・委譲に集中。「自分で worker 成果物を書かない」を志向に含める。

## 新規スキル追加時

1. **agent-creater** のみが `skills/<team>/<slug>/` を生成
2. `SKILL.md` + `personas/<slug>.md`（テンプレ上記 · **志向** 必須）
3. [`workflows/agent-registry.yaml`](../../workflows/agent-registry.yaml) 登録
4. 該当 `*-delivery.yaml` / `*-pm-assignment.md` / assign plan 更新
5. [`skill-persona-matrix.md`](../inventory/skill-persona-matrix.md) に 1 行追加
6. **検証:**

```powershell
python tools/check_new_skill.py --slug <slug> --department <team>
python tools/validate_org_registry.py
```

詳細: [`CONTRIBUTING.md`](../../CONTRIBUTING.md)

## 整備状況（v1.0）

| 領域 | persona 志向 | 備考 |
|------|--------------|------|
| UX v2 | ✅ 主要ロール | researcher は designer 兼担 |
| 分析 v2 | ✅ 全ロール | requirements-writer 含む |
| 開発 v3 | ✅ 全ロール | 本整備で更新 |
| 企画 | ✅ PM/planner/reviewer | 志向テンプレ適用 |
| 監査 | ✅ 最小 3 ロール | 志向テンプレ適用 |
| 組織改善 | ✅ 新設 | personas 追加 |

## 対応表（SSOT）

全 slug の SKILL · persona · 委譲関係: [`docs/inventory/skill-persona-matrix.md`](../inventory/skill-persona-matrix.md)

## 関連

- エージェント生成: [`skills/platform/agent-creater/SKILL.md`](../../skills/platform/agent-creater/SKILL.md)
- チーム索引: [`team-conventions.md`](team-conventions.md)
