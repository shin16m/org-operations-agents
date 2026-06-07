# developer smoke 提出テンプレ

| 版 | 1.0 |
| 日付 | 2026-06-08 |
| 適用 | developer complete 前必須 |
| 保存先 | `output/development/smoke/<parent_or_sub_gid>.md` |

## テンプレ

```markdown
# developer smoke — <task_gid>

| 項目 | 値 |
|------|-----|
| 実施日 | YYYY-MM-DD |
| 起動コマンド | `（設計書実行契約と同一）` |
| 起動 exit | 0 |

## Must AC 実行結果

| AC ID | 検証コマンド | exit | 結果抜粋 |
|-------|--------------|------|----------|
| AC-1 | `…` | 0 | … |

## 備考

（既知の未達 Should · 環境依存）
```

## ルール

- **passed 判定は developer が行わない** — 実行ログの提出のみ
- Must AC 全行を実行してから dev-reviewer へ code review 依頼
- smoke.md 欠落 → code review **failed**

## 関連

- [`acceptance-criteria-template.md`](acceptance-criteria-template.md)
- [`delivery-completion-standard.md`](delivery-completion-standard.md)
