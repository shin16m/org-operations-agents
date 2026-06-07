# notes 二層形式 — before / after

Epic: `1215474016466868` — Asana タスク説明に `## 依頼者向け` 必須化

## Before（legacy · 子タスク notes）

```markdown
チーム: development
状態: assigned

## 背景
Handoff 子の background フィールド全文（slug / GID 混在しやすい）。

## 概要
summary フィールド。

## 完了条件
done_when フィールド。
```

**問題:** 依頼者がタスクを開くと `## 背景` が先頭。専門用語中心で意図が読み取りづらい。

## After（v1.4 · 二層形式）

```markdown
チーム: development
状態: assigned

## 依頼者向け（人間が最初に読む）

summary を平易に記載した本文。

**完了すると:** done_when の要約

## 背景・用語（エージェント / 実装者向け）

### 背景
{background}

### 概要
{summary}

### 完了条件
{done_when}
```

**生成:** `assemble_subtask_notes()` in `asana_program_common.py`

**検証:**

```powershell
python tools/test_asana_notes_two_layer.py
python tools/validate_fixture_schemas.py
```

## 参照

- `docs/design/agent-asana-comment-signature.md` §6.1
- `docs/verification/fixtures/platform/handoff/handoff.requester-facing-notes.v1.json`
