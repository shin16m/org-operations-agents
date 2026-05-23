# platform — 横断スキル

L1 企画パイプライン・Asana 連携・配賦・メタ（agent-creater）。課内 delivery には入らない。

| slug | 役割 |
|------|------|
| workflow-orchestrator | intake / gate |
| asana-buddy | execute（Asana API） |
| task-dispatcher | dispatch |
| task-executor | work（deprecated） |
| agent-creater | 新規 `skills/<organization>/<slug>/` 生成 |

成果物: [`output/platform/`](../../output/platform/)
