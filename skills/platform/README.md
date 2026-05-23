# platform — 統括グループ

**統括グループ**（dispatch 対象外）。intake / bootstrap / dispatch 委譲・Asana 連携・メタ。

| slug | 役割 |
|------|------|
| workflow-orchestrator | intake / bootstrap / dispatch 委譲 |
| asana-buddy | Asana API（bootstrap / 本番投入 / 読取 / 完了） |
| task-dispatcher | チームへのルーティング |
| agent-creater | 新規 `skills/<organization>/<slug>/` 生成 |

成果物: [`output/platform/`](../../output/platform/)

設計: [`docs/design/department-model.md`](../../docs/design/department-model.md)
