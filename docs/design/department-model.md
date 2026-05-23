# 組織モデル — チーム・統括グループ・チーム間 I/O

## 組織の種類

| 種類 | 例 | 役割 |
|------|-----|------|
| **チーム** | 企画チーム / 開発チーム / 分析チーム | 自律した delivery。チーム内 workflow と I/O を自分で決める |
| **統括グループ** | workflow-orchestrator, task-dispatcher, asana-buddy, agent-creater | **配線・メタ**。チーム内業務は持たない。dispatch 対象外 |

スキル配置: チーム → `skills/<department>/` · 統括グループ → `skills/platform/`（パス slug は `platform` のまま。表示名は **統括グループ**）

登録: [`workflows/organizations.yaml`](../../workflows/organizations.yaml)

---

## 原則

1. **チーム内自律** — 段階・役割・レビューは各チームの `*-delivery.yaml` が決める
2. **チーム間は契約のみ** — チームをまたぐ公式 I/O は下表に限定する
3. **Handoff JSON はチーム間 I/O に使わない** — 企画チームの**チーム内**成果物。他チームは読まない
4. **統括グループは配線** — intake / bootstrap / dispatch / Asana CRUD。業務判断はチーム PM へ

---

## チーム間 I/O（公式）

| 方向 | 形式 | 説明 |
|------|------|------|
| 統括グループ → チーム | `DispatchRequest` | `task_gid` + `department` |
| 統括グループ → チーム | **Asana 子タスク + notes** | 背景・概要・完了条件・`チーム:` 行 |
| チーム → 統括グループ | `DeptWorkComplete` | 子 1 件の完了報告 |
| チーム → 統括グループ | Asana `comment_task` + `complete_task` | 署名付き記録と完了同期 |

**チーム間 I/O に含めないもの**

- `AsanaBuddyHandoff` JSON ファイル（企画チーム内部）
- `PlanReviewResult`（企画チーム内部）
- 他チームの `output/<dept>/` 成果物の直接参照（必要なら PM が notes に要約を書く）

**統括グループ / チーム PM の運用ツール（チーム間 I/O ではない）**

- `sync_handoff_epic.py --handoff` — Handoff の子タイトル【n/m】と Asana を照合し一括完了する **Asana 同期**用。要件の受け渡しには使わない。
- bootstrap 用 Handoff JSON — 統括グループが L1 で企画子 1 件を Asana に作成するための**内部成果物**。他チーム PM は読まず、反映済み notes を読む。

企画チームが他チームへ渡す情報は、**Asana 上の親・子タスクと notes** に落とした時点で公式化する。

---

## チームの追加ルール（必須 4 点セット）

新規チーム（例: 運用チーム）を足すとき:

| # | 成果物 | 例 |
|---|--------|-----|
| 1 | [`workflows/organizations.yaml`](../../workflows/organizations.yaml) | `departments[]` に 1 行 |
| 2 | `workflows/<id>-delivery.yaml` | チーム内 workflow |
| 3 | `docs/design/<id>-delivery-io.md` | チーム内 I/O + チーム間 I/O + やらないこと |
| 4 | PM ハブスキル | `skills/<dept>/<dept>-pm/`（`dept_orchestrate`） |

追加: チーム内ワーカー・reviewer を `agent-registry.yaml` に登録。統括グループの変更は通常不要。

---

## 既存チーム一覧

| id | ラベル | workflow | PM ハブ | I/O 文書 |
|----|--------|----------|---------|----------|
| `planning` | 企画チーム | `planning-delivery` | planning-pm | [`planning-delivery-io.md`](planning-delivery-io.md) |
| `development` | 開発チーム | `development-delivery` | product-manager | [`development-delivery-io.md`](development-delivery-io.md) |
| `analysis` | 分析チーム | `analysis-delivery` | analytics-pm | [`analysis-delivery-io.md`](analysis-delivery-io.md) |

チーム間共通契約: [`dept-work-io.md`](dept-work-io.md)（`DispatchRequest` / `DeptWorkComplete`）

---

## 三層レイヤー（参照）

```
統括グループ: intake → bootstrap → dispatch 委譲
       ↓
チーム（L3）: PM ハブ → チーム内 workflow → DeptWorkComplete
       ↓
統括グループ: 次の子 dispatch / エピック完了集約
```

詳細: [`org-dispatch-model.md`](org-dispatch-model.md)
