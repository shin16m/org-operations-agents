# 承認フロー再設計 C — Ready 再開ループと NG 差し戻し — delivery

> **履歴（RETIRED · 2026-06-09）** — 再開ループ CLI 削除済。本番は [chat-driven-ops.md](../../design/chat-driven-ops.md) · [approval-flow.md](../../design/approval-flow.md)（C 段階 RETIRED）。

| 項目 | 値 |
|------|------|
| Asana 親 epic | `1215089810887005` |
| Source Intake | `1215102436390998` |
| 関連 (A 完了 / B 完了) | `1215102436561886` / `1215102437909462` |
| 完了日 | 2026-05-25 |
| profile | lite |

## 概要

承認フロー再設計 3 分割の **C（締め）**。B が親 epic を `OS State=Ready · Approval Required=No` に戻した後の Ready 再開と、`Approval Result=NG` 時のループ・上限制御を担う resume scanner CLI を新設。3 分割すべて完了で承認フロー再設計 epic 群を終結。

## 変更点

### 実装

| ファイル | 変更 |
|---------|------|
| `tools/wakuoke_resume_scan.py` | **新規** — 4 ケース分岐（fresh / OK / NG / ESCALATE）+ NG counter 永続化 + escalation コメント投稿 |
| `tools/approval_helper.py` | ログ JSON に `consumed: false` 初期値を追加（C スキャナが二重カウント防止のため）|

### SSOT

| ファイル | 変更 |
|---------|------|
| `docs/design/approval-flow.md` | §5 表で C 実装済化 + §5.3 resume scanner CLI 仕様（出力語彙 / 処理フロー / NG counter / consumed フラグ / スコープ外）|
| `docs/design/asana-driven-ops.md` | Tools 表に `wakuoke_resume_scan.py` 追加 |
| `skills/platform/asana-buddy/SKILL.md` | `wakuoke_resume_scan.py` 追記 |
| `skills/platform/workflow-orchestrator/SKILL.md` §F | B/C 連動運用 + NG ループ運用方針追記 |

## 出力語彙（resume scanner）

| 行頭 | 意味 |
|------|------|
| `SCAN` | スキャン開始 |
| `READY` | Ready epic でヘルパーログ無し（fresh dispatch lane） |
| `RESUME` | Ready epic で `consumed=false` ヘルパーログあり、再開可能 |
| `ESCALATE` | NG 上限到達、親 epic に escalation コメント投稿 |
| `DONE` | スキャン完了サマリ |

## 受け入れ条件

| # | 条件 | 結果 |
|---|------|------|
| 1 | `--dry-run` がエラー無く終了 | ✅ |
| 2 | fresh / OK / NG / NG-上限 4 ケースで適切な行を出力 | ✅ fixture で確認 |
| 3 | NG counter JSON が永続化（history 含む） | ✅ |
| 4 | `--dry-run` で escalation コメント投稿しない | ✅ |
| 5 | CF/env 未設定で停止しない | ✅ コードで確認 |
| 6 | `validate_ssot_contract.py` 通過 | ✅ |

## レビュー結果

| review | status |
|--------|--------|
| `output/development/reviews/1215089844826895-code.review.json` | passed |
| `output/development/reviews/1215089844826895-verification.review.json` | passed |
| `output/governance/reviews/1215089844814399-governance.review.json` | passed |
| `output/audit/reviews/1215089670482421-audit.review.json` | passed |

## 承認フロー再設計 — 全体まとめ（A + B + C）

| Epic | 範囲 | 完了 |
|------|------|------|
| **A** Approval Result CF + 人間 assignee 連携 | 起票時の書込み（OS State=Waiting / Approval Required=Yes / 人間 assignee）+ Approval Result CF env 同期 | ✅ 2026-05-25 |
| **B** 承認ヘルパー | `tools/approval_helper.py` で完了監視 + 親 CF 戻し + ログ JSON | ✅ 2026-05-25 |
| **C** Ready 再開ループ | `tools/wakuoke_resume_scan.py` で fresh / OK / NG / ESCALATE 分岐 + NG counter 永続化 | ✅ 2026-05-25 |

## 運用フロー（A → B → C 連携）

```
[planning gate]
   │ create_approval_subtask（A）
   ▼
[親 OS State=Waiting + Approval Required=Yes + 人間 assignee 設定済]
   │ 依頼者が Asana UI で Approval Result=OK/NG 選択 + 完了
   ▼
[承認サブ completed]
   │ approval_helper.py --once（B）
   ▼
[親 OS State=Ready + Approval Required=No · ログ JSON 保存（consumed=false）]
   │ wakuoke_resume_scan.py --dry-run（C）
   ▼
[RESUME (OK / NG count<max) / ESCALATE (NG count>=max)]
   │ 和久桶セッション人間判断
   ▼
[execution dispatch / NG 修正再投入 / 依頼者エスカレーション]
```

## 関連リンク

- 設計 SSOT: [`docs/design/approval-flow.md`](../design/approval-flow.md) §5.3
- A delivery: [`approval-redesign-a-delivery.md`](approval-redesign-a-delivery.md)
- B delivery: [`approval-redesign-b-delivery.md`](approval-redesign-b-delivery.md)
- Handoff: `output/planning/handoff/handoff.approval-redesign-c.json`
- Plan review: `output/planning/plan-review/plan-review.approval-redesign-c.json`
