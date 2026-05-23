# 組織モデル・子タスク単位ディスパッチ・完了集約

**SSOT:** [`department-model.md`](department-model.md)（チーム間 I/O・チーム追加ルール・統括グループ）

## 三層レイヤー

```
┌─────────────────────────────────────────────────────────────┐
│ L1 受付（統括グループ）                                       │
│   workflow-orchestrator → bootstrap → dispatch（企画チーム）      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ L2 配賦（統括グループ）                                       │
│   task-dispatcher — 子 task_gid + department                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ L3 チーム内（企画 / UX / 開発 / 分析）                            │
│   PM ハブ → チーム内 workflow → DeptWorkComplete                  │
│   チーム間共有: Asana 子 + notes（Handoff JSON は使わない）        │
└─────────────────────────────────────────────────────────────┘
```

## 配賦単位

| 項目 | ルール |
|------|--------|
| ディスパッチ単位 | Asana **子タスク 1 件** |
| チーム内 workflow | 子ごとに**独立インスタンス** |
| チーム間入力 | **Asana notes** + `DispatchRequest` |
| 配賦順序 | 企画子 → 企画完了後 **ux（Web・UI 先行）** → development / analysis 子 |

## 責務表

| 役割 | 所属 | やること | やらないこと |
|------|------|----------|--------------|
| **workflow-orchestrator** | 統括グループ | intake / bootstrap / dispatch 委譲・集約 | チーム内業務 |
| **task-dispatcher** | 統括グループ | チームへルーティング | チーム内作業 |
| **asana-buddy** | 統括グループ | Asana CRUD | 作業本体 |
| **planning-pm** | 企画チーム | Handoff → review → Asana タスク化 | 他チーム実装 |
| **ux-pm** | UX チーム | タスク分解・アサイン・UX delivery | 実装 |
| **product-manager** | 開発チーム | 開発 delivery | Handoff 作成 |
| **analytics-pm** | 分析チーム | 分析 delivery | Handoff 作成 |

## 関連

- チーム I/O: `planning-delivery-io.md` / `ux-delivery-io.md` / `development-delivery-io.md` / `analysis-delivery-io.md`
- チーム間共通: [`dept-work-io.md`](dept-work-io.md)
- 新チーム追加: [`new-department-checklist.md`](new-department-checklist.md)
- ルーティング: [`workflows/organizations.yaml`](../../workflows/organizations.yaml)
