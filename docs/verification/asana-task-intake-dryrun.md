# Asana タスク起点 intake — dryrun 記録

| 項目 | 内容 |
|------|------|
| エピック GID | `1215085626249358` |
| development 子 | `1215085681753358` |
| 日付 | 2026-05-24 |

## 目的

Asana タスク URL / GID を和久桶さん（workflow-orchestrator）に渡し、既存 workflow で処理開始する **intake-asana** 窓口を検証する。

## 手順

### 1. snapshot 取得（GID）

```powershell
python tools/intake_from_asana.py --task 1215085626249358
```

### 2. snapshot 取得（URL）

```powershell
python tools/intake_from_asana.py --task "https://app.asana.com/1/1214766054680431/project/1214771428861230/task/1215085626249358"
```

### 3. ファイル出力

```powershell
python tools/intake_from_asana.py --task 1215085626249358 --out output/platform/intake/1215085626249358-snapshot.json
```

### 4. orchestrator intake-asana（Cursor 起動例）

```
あなたは workflow-orchestrator スキルです（intake-asana モード）。
Asana タスク: 1215085626249358
intake_from_asana.py で読取 → bootstrap Handoff → dispatch（企画チーム）まで進めてください。
```

## 期待結果

- exit 0 · JSON に `schema_version: "1.1"`（`--no-comments` 時は `"1.0"`）· `task_gid` · `name` · `notes`
- v1.1: `comments[]` / `comments_markdown`（ユーザーコメント story のみ）
- GID / URL 両方で同一タスクを取得
- 403/404 時は stderr に権限・存在エラーメッセージ（exit 3）

## 本エピックでの実施

- intake → bootstrap → planning gate → asana_execute → development lite → audit
- `tools/intake_from_asana.py` 新規 · orchestrator SKILL 起動例 C · workflow-session-io 拡張

## 参照

- [`skills/platform/workflow-orchestrator/SKILL.md`](../../skills/platform/workflow-orchestrator/SKILL.md) — 起動例 C
- [`docs/design/workflow-session-io.md`](../design/workflow-session-io.md)
