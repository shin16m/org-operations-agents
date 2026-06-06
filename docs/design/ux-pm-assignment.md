# ux-pm 厳密運用 — チーム内アサインと delivery profile

| 版 | 2.0 |
| 日付 | 2026-06-06 |
| 適用 | UX チーム L3（`ux-delivery` v2） |

## 原則

1. **ux-pm は自分で体験設計・Figma 作成しない**（進行・タスク分解・artifact 公開・完了集約を除く）。
2. PM が dispatch された子タスクを読み、**delivery profile** を決め、**workflow フェーズごとに作業単位を洗い出す**。
3. **必須:** 洗い出したフェーズを **Asana サブタスク** に分解し、各 notes に **担当 slug**（と `profile:`）を書く（単一タスクに PM 以外を直接委譲しない）。
4. **担当エージェントだけ**がそのサブタスクを実行する（notes の `担当:` と自分の slug が一致すること）。
5. 完了は **担当の comment_task → PM が当該サブを complete → 全サブ完了後に親を comment → complete**。

**comment_task:** PM slug で ux-designer / design-system-owner / ux-reviewer の作業を署名しない。

開発チーム同等運用: [`development-pm-assignment.md`](development-pm-assignment.md) · 強みの型: [`delivery-strength-pattern.md`](delivery-strength-pattern.md)

## PM の必須フロー（intake）

```
1. fetch_task.py --gid <親子GID> で notes を読む
2. delivery profile を決定（省略時 standard）
3. profile に応じたフェーズ一覧を assign plan JSON に落とす
4. pm_assign_subtasks.py でサブタスク作成 + 各 担当: 設定
5. **デフォルト:** gate 省略 → **check_pm_review_gate.py** exit 0（gate 無し）→ L3b  
   **opt-in**（`human_review_gate: true` / `--require-human-review` / `ORG_OPS_PM_REVIEW_GATE=1`）: **create_pm_review_gate.py** → 人間 complete → check exit 0
6. 親 notes → 担当: ux-pm, 状態: in_progress, profile: <決定値>
7. サブ完了のたびに次フェーズを確認し、全サブ完了後に DeptWorkComplete
```

**禁止:** サブタスクを作らず、親タスク notes の `担当:` だけ ux-designer に書き換えて委譲すること。

**dispatch 起動文 SSOT:** [`dispatch-prompt-ssot.md`](dispatch-prompt-ssot.md#ux)

## PM が書いてはいけない成果物（ワーカー専用）

| 種別 | パス | 担当 slug |
|------|------|-----------|
| Figma UI | Figma ファイル URL | ux-designer |
| 体験設計 companion | `output/ux/specs/<sub_gid>-ux-spec.md` | ux-designer |
| Design System | `output/ux/design-system/<sub_gid>-design-system.md` | design-system-owner |
| Code Connect | `output/ux/code-connect/<parent_gid>/` | design-system-owner |
| レビュー | `output/ux/reviews/` | ux-reviewer |

## notes ヘッダ（必須・先頭）

### 親（進行タスク）

```markdown
チーム: ux

profile: standard
担当: ux-pm
状態: in_progress

```

### サブ（委譲タスク）

```markdown
チーム: ux

profile: flagship
担当: ux-designer
状態: assigned

```

| フィールド | 値 |
|------------|-----|
| `チーム` | `ux` |
| `profile` | `flagship` \| **`standard`** \| `lite`（親で決定。サブは省略可＝親継承） |
| `担当` | [`agent-registry.yaml`](../../workflows/agent-registry.yaml) の slug |
| `状態` | `assigned` \| `in_progress` \| `review` \| `done` |

## delivery profile

| profile | スキップする段階 | 備考 |
|---------|------------------|------|
| **`flagship`** | なし | **Figma 複数案（2+）必須** · design_quality 必須 |
| **`standard`** | なし | Figma UI + DS 必須 |
| **`lite`** | ux-designer Figma 新規 · design_quality · design-system-owner | 既存 DS 参照 · spec 更新のみ |

### profile 選定ガイド

| 依頼のキーワード・状況 | 推奨 profile | 避ける profile |
|------------------------|--------------|----------------|
| 新規 Web アプリ · ランディング · ブランド体験 | **flagship** | lite |
| 画面追加・既存アプリの改修 | **standard** | lite |
| 文言変更 · 既存 DS 内の微調整 | **lite** | flagship |
| org-meta · 本リポジトリのみ | —（UX 子不要） | — |

**判断の順序:** (1) 新規ビジュアルが要るか → flagship or standard / (2) 既存 DS 流用か → lite

## サブタスク分解（例 — standard / flagship）

親: `【2/4・UX】Web アプリ体験設計` — **担当: ux-pm**

| サブ | 担当 | 成果物 |
|------|------|--------|
| 【2/4-1】Figma UI | ux-designer | Figma URL + `output/ux/specs/<gid>-ux-spec.md` |
| 【2/4-2】design quality review | ux-reviewer | `review_kind: design_quality` |
| 【2/4-3】Design System | design-system-owner | Figma DS + `output/ux/design-system/<gid>-design-system.md` |
| 【2/4-4】仕様 review | ux-reviewer | `review_kind: ux_spec` |

プラン例:
- [`skills/ux/examples/assign-plan.web-app-flagship-v2.json`](../../skills/ux/examples/assign-plan.web-app-flagship-v2.json)
- [`skills/ux/examples/assign-plan.web-app-v1.json`](../../skills/ux/examples/assign-plan.web-app-v1.json)（legacy v1 参考）

**flagship 追加要件:** 【2/4-1】の done_when に「**2 案以上の Figma フレーム**と選定理由」を含める。

## 委譲先一覧（workflow 段階）

| 段階 | 担当 slug | 備考 |
|------|-----------|------|
| Figma UI + ux-spec | ux-designer | flagship は複数案 |
| design quality | ux-reviewer | `review_kind: design_quality` · lite 除く |
| Design System | design-system-owner | lite 除く |
| 仕様 review | ux-reviewer | `review_kind: ux_spec` |
| 実装一致 review | ux-reviewer | `review_kind: ux_implementation` — **product-manager** から委譲 |

## CLI

```powershell
.\.venv\Scripts\python.exe .\skills\platform\asana-buddy\optional\pm_assign_subtasks.py `
  --parent <親GID> --plan .\skills\ux\examples\assign-plan.web-app-flagship-v2.json `
  --department ux --update-parent-assignee ux-pm -y
```

## L3b — ワーカー dispatch（必須）

```powershell
python tools/pm_emit_worker_prompt.py --parent <親GID> --department ux
```

SSOT: [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md)

## レビュー NG 時（修正タスク）

[`pm-review-rework-ssot.md`](pm-review-rework-ssot.md) · `python tools/pm_create_fix_subtask.py --parent <GID> --review-json output/ux/reviews/<file>.json -y`

## 参照

- [`ux-delivery-io.md`](ux-delivery-io.md)
- [`cross-team-artifact-bridge.md`](cross-team-artifact-bridge.md)
- [`skills/ux/ux-pm/SKILL.md`](../../skills/ux/ux-pm/SKILL.md)
