# analytics-pm 厳密運用 — チーム内アサインと delivery profile

| 版 | 2.0 |
| 日付 | 2026-06-06 |
| 適用 | 分析チーム L3（`analysis-delivery` v2） |

## 原則

1. **analytics-pm は自分で要件書・データ設計・実装・モデルを書かない**（進行・分解・完了集約のみ）。
2. PM が dispatch された子タスクを読み、**delivery profile** を決め、**workflow フェーズごとに作業単位を洗い出す**。
3. **必須:** フェーズを **Asana サブタスク** に分解し、各 notes に **担当 slug**（と `profile:`）を書く。
4. **担当エージェントだけ**がそのサブタスクを実行する。
5. 完了は **担当の comment_task → PM が当該サブを complete → 全サブ完了後に親を comment → complete**。

開発チーム同等: [`development-pm-assignment.md`](development-pm-assignment.md) · 強みの型: [`delivery-strength-pattern.md`](delivery-strength-pattern.md)

## PM の必須フロー（intake）

```
1. fetch_task.py --gid <親子GID> --show-assignee
2. delivery profile を決定（省略時 full）
3. profile に応じたフェーズ一覧を assign plan JSON に落とす
4. pm_assign_subtasks.py --department analysis --update-parent-assignee analytics-pm -y
5. **デフォルト:** gate 省略 → **check_pm_review_gate.py** exit 0（gate 無し）→ L3b  
   **opt-in**（`human_review_gate: true` / `--require-human-review` / `ORG_OPS_PM_REVIEW_GATE=1`）: **create_pm_review_gate.py** → 人間 complete → check exit 0
6. 親 notes → 担当: analytics-pm, 状態: in_progress, profile: <値>
7. 全サブ完了後 DeptWorkComplete（artifacts[] に下流参照を含める）
```

**dispatch 起動文:** [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md#analysis)

## PM が書いてはいけない成果物

| 種別 | パス | 担当 slug |
|------|------|-----------|
| 分析要件 | `output/analysis/requirements/<gid>-requirements.md` | analytics-requirements-writer |
| データ設計 | `output/analysis/data-model/<gid>.md` | data-architect |
| パイプライン | 別リポジトリ / `pipelines/` | data-engineer |
| カタログ | `output/analysis/catalog/<gid>.md` | data-steward |
| インサイト | `output/analysis/insights/<gid>.md` | data-analyst |
| モデル | `output/analysis/models/<gid>/` | data-scientist |
| デプロイ | `deploy/<gid>/` | ml-engineer |
| リリース | `output/analysis/releases/<gid>-release.md` | analytics-requirements-writer |
| レビュー | `output/analysis/reviews/` | analysis-reviewer |

## notes ヘッダ（必須・先頭）

### 親

```markdown
チーム: analysis

profile: full
担当: analytics-pm
状態: in_progress

```

### サブ

```markdown
チーム: analysis

profile: model-serve
担当: data-architect
状態: assigned

```

| フィールド | 値 |
|------------|-----|
| `チーム` | `analysis` |
| `profile` | `full` \| `model-serve` \| `insights` \| `catalog` \| `lite` |
| `担当` | registry slug |
| `状態` | `assigned` \| `in_progress` \| `review` \| `done` |

## delivery profile

| profile | 用途 | 主なフェーズ | スキップ |
|---------|------|--------------|----------|
| **`full`** | 要件→本番デプロイまで一気通貫 | 全フェーズ | なし |
| **`model-serve`** | 推論 API/モデルを開発が consume | 要件→設計→ETL→品質→モデル→gate→デプロイ | exploration |
| **`insights`** | BI・ダッシュボード・探索のみ | 要件→設計→ETL→品質→探索 | model, gate, ml-engineer |
| **`catalog`** | データカタログ・SLA・ガバナンス | 要件→設計→品質 | ETL, 探索, model, deploy |
| **`lite`** | カタログ/ルールの小更新 | steward または architect + review | 大半 |

### profile 選定ガイド

| 依頼のキーワード | 推奨 profile | 避ける profile |
|------------------|--------------|----------------|
| 本番モデル · API · MLOps · 推論 | **model-serve** または **full** | insights |
| ダッシュボード · レポート · 探索分析 | **insights** | model-serve |
| データカタログ · SLA · 品質ルール | **catalog** | model-serve |
| ルール 1 件修正 · メタデータ追記 | **lite** | full |
| 初回データ基盤 + モデル + 運用 | **full** | lite |

**判断順序:** (1) 開発がモデル/API を consume するか → model-serve/full / (2) 画面・BI のみか → insights / (3) カタログのみか → catalog / lite

### ml-engineer 着手条件（全 profile 共通）

- `production_deploy_gate` が `passed*`（insights / catalog / lite では N/A）
- PM が gate 未通過で ml-engineer サブを作らない

## assign plan 例

| profile | パス |
|---------|------|
| full（dryrun） | [`skills/analysis/examples/assign-plan.dryrun-v2.json`](../../skills/analysis/examples/assign-plan.dryrun-v2.json) |
| model-serve | [`skills/analysis/examples/assign-plan.model-serve-v2.json`](../../skills/analysis/examples/assign-plan.model-serve-v2.json) |
| insights | [`skills/analysis/examples/assign-plan.insights-v2.json`](../../skills/analysis/examples/assign-plan.insights-v2.json) |
| catalog | [`skills/analysis/examples/assign-plan.catalog-v2.json`](../../skills/analysis/examples/assign-plan.catalog-v2.json) |

## L3b — ワーカー dispatch

```powershell
python tools/pm_emit_worker_prompt.py --parent <親GID> --department analysis
```

## 下流公開（開発チーム）

完了時 `DeptWorkComplete.artifacts[]` に安定 ID を含め、開発 PM が notes `## 依存` へ転記。テンプレ: [`cross-team-artifact-bridge.md`](cross-team-artifact-bridge.md#分析--開発)

## レビュー NG 時

[`pm-review-rework-ssot.md`](pm-review-rework-ssot.md) · `python tools/pm_create_fix_subtask.py --parent <GID> --review-json output/analysis/reviews/<file>.json [--fix-assignee <slug>] -y`

## 参照

- **worker dispatch:** [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md)
- **review NG:** [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md)
- [`analysis-delivery-io.md`](analysis-delivery-io.md)
- [`skills/analysis/analytics-pm/SKILL.md`](../../skills/analysis/analytics-pm/SKILL.md)
