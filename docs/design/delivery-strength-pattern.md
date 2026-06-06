# Delivery 強みの型 — 開発チーム基準の共通テンプレ

| 版 | 1.0 |
| 日付 | 2026-06-06 |
| 参照実装 | 開発チーム `development-delivery` v3 |
| 最初の展開先 | UX チーム `ux-delivery` v2 |

## 目的

開発チームの見直しで確立した運用強みを、**チーム特性に応じて適用可能な共通パターン**として言語化する。全チームを同一粒度に揃えることは目的としない。

## 4 つの共通プリミティブ

### 1. delivery profile（深さの出し分け）

| 要素 | 説明 |
|------|------|
| **何を決めるか** | 子タスク 1 件に対し、どのフェーズを厚く・薄く走らせるか |
| **誰が決めるか** | チーム PM（intake 時） |
| **どこに書くか** | 親子 notes 先頭 `profile: <値>` |
| **参照** | 開発: [`development-pm-assignment.md`](development-pm-assignment.md) · UX: [`ux-pm-assignment.md`](ux-pm-assignment.md) |

**原則:** profile なし = チームの `standard`（既定）とみなす。Epic 全体ではなく **子タスク単位**で決める。

### 2. フェーズ分解 + PM/worker 分離（L3b）

| 要素 | 説明 |
|------|------|
| **何をするか** | workflow フェーズごとに Asana サブタスクを切り、各 `担当:` をワーカー slug に固定 |
| **PM の境界** | 進行・分解・アサイン・完了集約のみ。ワーカー成果物は **別セッション**（`pm_emit_worker_prompt.py`） |
| **禁止** | 親タスクの `担当:` 書き換えのみでの委譲 · PM がワーカー成果物を代行 |
| **参照** | [`pm-worker-dispatch-ssot.md`](pm-worker-dispatch-ssot.md) · [`pm-worker-separation-enforcement.md`](pm-worker-separation-enforcement.md) |

### 3. 多段ゲート + 修正サブ新規（反復前提）

| 要素 | 説明 |
|------|------|
| **ゲート** | 各フェーズに reviewer / verifier。`passed*` でのみ次へ |
| **NG 時** | 修正サブタスクを **新規追加** → 再 review サブ。完了タスクの `--undo` 禁止 |
| **参照** | [`pm-review-rework-ssot.md`](pm-review-rework-ssot.md) |

**チームごとのゲート例:**

| チーム | ゲート（例） |
|--------|--------------|
| 開発 | requirements / design / code / ux_implementation / verification / mismatch |
| UX v2 | design_quality / ux_spec |
| 分析 | doc / deploy gate |
| 監査 | audit_review_passed |

### 4. 成果物の安定 ID + 下流 consume 契約

| 要素 | 説明 |
|------|------|
| **命名** | `output/<dept>/.../<task_gid>-<kind>.<ext>` |
| **完了時** | `DeptWorkComplete.artifacts[]` に安定パスを列挙 |
| **下流** | consume 側 PM が notes `## 依存（読み取り専用）` へ転記してから着手 |
| **参照** | [`department-model.md`](department-model.md#成果物共有読み取り専用) · [`cross-team-artifact-bridge.md`](cross-team-artifact-bridge.md) |

## チームへの適用マトリクス

| チーム (`id`) | profile | フェーズ分解 | 多段ゲート | artifact bridge | 優先度 |
|--------|---------|--------------|------------|-----------------|--------|
| 開発 (`development`) | ✅ v3 | ✅ | ✅ | UX/分析 consume | 基準（完了） |
| UX (`ux`) | ✅ v2 | ✅ | ✅ v2 拡張 | → 開発 full-ui | 完了 |
| 分析 (`analysis`) | ✅ v2 | ✅ | ✅ | → 開発 model-serve | 完了 |
| 企画 | 別モデル（Handoff） | ✅ | review + 人間 gate | Asana タスク化 | 維持 |
| 組織改善 | lite 相当 | ✅ | ✅ | org-meta | 維持 |
| 監査 | 単一 | ✅ | ✅ | — | 維持 |

## 新チーム / ロール追加時のチェックリスト

### 新チーム（department）

1. [`new-department-checklist.md`](new-department-checklist.md) A〜J
2. `python tools/check_new_department.py --department <id>`

### 新ロール（既存チーム内）

1. [`skill-persona-principles.md`](skill-persona-principles.md) — agent-creater → SKILL + persona（志向）
2. `*-delivery.yaml` / `*-pm-assignment.md` / assign plan 更新
3. [`skill-persona-matrix.md`](../inventory/skill-persona-matrix.md) に 1 行
4. `python tools/check_new_skill.py --slug <slug> --department <dept>`

### 共通（L3 delivery）

1. PM ハブ + `*-pm-assignment.md`（profile · `human_review_gate` opt-in · pm_assign 必須）
2. `*-delivery.yaml` にゲートとフェーズを宣言
3. `*-delivery-io.md` に成果物パスと下流公開形式（[`cross-team-artifact-bridge.md`](cross-team-artifact-bridge.md)）
4. assign plan 例を `skills/<dept>/examples/` に追加
5. dryrun: `docs/verification/*dryrun*.md` または `tools/run_*dryrun*.py`
6. `agent-registry.yaml` 登録 → `python tools/validate_org_registry.py`

## 関連

- スキル・ペルソナ: [`skill-persona-principles.md`](skill-persona-principles.md)
- 組織モデル: [`department-model.md`](department-model.md)
- チーム索引: [`team-conventions.md`](team-conventions.md)
- UX v2: [`ux-delivery-io.md`](ux-delivery-io.md)
- 分析 v2: [`analysis-delivery-io.md`](analysis-delivery-io.md)
