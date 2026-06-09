# Asana Task Type カスタムフィールド — 運用 SSOT

| 版 | 1.1 |
| 日付 | 2026-05-24 |
| エピック | `1215089212767842` · poller 更新 `1215089353199032` |

## 目的

Asana プロジェクトの **Task Type** enum CF で、タスクが **Intake（依頼入口）** か **Epic（org-ops エピック）** かを判別する。

| 値 | 意味 |
|----|------|
| **Intake** | 依頼者が和久桶さん（workflow-orchestrator）へ渡す **入口タスク** |
| **Epic** | org-ops が bootstrap / handoff で作成する **親エピック** |

## 和久桶さん（workflow-orchestrator）起票ルール

| 起票種別 | Task Type | Agent Type | 備考 |
|----------|-----------|------------|------|
| **Intake**（依頼者→和久桶入口） | **Intake** | **AI** | チャットで和久桶に URL 手動渡し時の参照用（**自動検出廃止**） |
| **Epic**（bootstrap / handoff 親） | **Epic** | **AI** | `handoff_to_asana.py` create 時に org-ops が自動設定 |

**Intake タスク作成（依頼者が Asana UI で起票）:**

- Task Type = **Intake**
- Agent Type = **AI**

**Intake タスク（手動 intake-asana · 自動検出は廃止）:**

- 未完了 · トップレベル
- **Agent Type = AI** かつ **Task Type = Intake**

**Epic タスク作成（和久桶 bootstrap）:**

- `handoff_to_asana.py` create モードが **Agent Type=AI · Task Type=Epic · OS State=Ready** を設定
- 手動で epic を作る場合も同じ CF 組み合わせを守る

## org-os watch 対象 — RETIRED

> **廃止（2026-06-09）** — org-os watch は本番で使わない。

~~`org-os watch --project <GID>` が列挙するタスク:~~

1. **Agent Type** = `AI`
2. **Task Type** = `Epic`
3. **OS State** = `Ready` または `Waiting`

上記を満たさないタスクは `skipped` としてカウントされる。

## env 同期

```powershell
python tools/sync_task_type_env.py --project <PROJECT_GID> --dry-run
python tools/sync_task_type_env.py --project <PROJECT_GID> --write -y
```

| env キー | 内容 |
|---------|------|
| `ASANA_TASK_TYPE_FIELD_GID` | Task Type フィールド GID |
| `ASANA_TASK_TYPE_INTAKE_GID` | enum `Intake` |
| `ASANA_TASK_TYPE_EPIC_GID` | enum `Epic` |

テンプレート: [`skills/platform/asana-buddy/optional/.env.example`](../../skills/platform/asana-buddy/optional/.env.example)

## GID（プロジェクト `1214771428861230`）

| 種別 | GID |
|------|-----|
| フィールド「Task Type」 | `1215089213221082` |
| enum `Intake` | `1215089213221083` |
| enum `Epic` | `1215089213221084` |

## org-ops 自動設定

| CLI / 関数 | Task Type |
|------------|-----------|
| `handoff_to_asana.py` 親タスク create | **Epic** |
| `set_task_type_epic` / `set_task_type(..., "Epic")` | **Epic** |
| intake 元タスク（依頼者作成） | **Intake**（手動 · Agent Type 未設定） |

## 参照

- Agent Type: [`asana-assignee-type-field.md`](asana-assignee-type-field.md)
- org-os 境界: [`org-os-product-io.md`](org-os-product-io.md)
- 和久桶 SKILL: [`skills/platform/workflow-orchestrator/SKILL.md`](../../skills/platform/workflow-orchestrator/SKILL.md)
