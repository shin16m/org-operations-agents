# 監査網羅 validate 拡張 + 新 department チェックリスト機械化 — 設計

| 項目 | 内容 |
|------|------|
| エピック | `1215085625536981` |
| 子 | A2 `1215085751484161`（development · lite）· audit `1215085625658246` |
| スコープ外 | A（`organizations.yaml` → schema enum 自動生成） |

## 背景

監査チーム追加・intake 方針追加で **5 連続 SSOT 修正コミット**が発生。`department` 一覧が **8 箇所に分散**し、`validate_org_registry.py` は**存在チェック止まり**。`new-department-checklist.md` は**手動チェック**。

## A2 — `validate_org_registry.py` に追加する 5 系統

| # | 対象 | チェック内容 |
|---|------|-------------|
| A2-1 | `README.md` | 「N チーム」表記が enabled department 数と一致 |
| A2-2 | `docs/verification/README.md` | 「N チーム」表記が enabled department 数と一致 |
| A2-3 | `tools/run_all_teams_dryrun.py` | `DEPT_PM` キーが **execution 系 4 department**（planning / ux / development / analysis）を含む。`audit` は組織変更時のみのため任意 |
| A2-4 | `docs/design/agent-asana-comment-signature.md` | enabled 全 department の **PM slug**（`organizations.yaml.entry_agent`）が記載 |
| A2-5 | `.cursor/rules/workflow-intake-required.mdc` | 全 enabled department id が記載（チーム表 + 配賦順） |

### 仕様メモ

- 「N チーム」抽出は `(\d+)\s*チーム` 正規表現。複数ヒット時は **最大値** を使う
- PM slug は `organizations.yaml` の `entry_agent` を権威とする（registry の `dept_orchestrate` slot ではなく）
- A2-3 の「execution 系 4」は `set(dept_ids) - {"audit"}` と表現

## B — `tools/check_new_department.py` が走査する項目

`--department <id>` で `new-department-checklist.md` の **A〜F 必須行**を機械チェック。

### B 対応表（チェックリスト ID → 機械チェック内容）

| ID | 対象 | チェック |
|----|------|---------|
| A1 | `workflows/organizations.yaml` | `- id: <id>` 行が存在 |
| A2 | `workflows/<id>-delivery.yaml` | ファイル存在 + `entry_agent:` 行 + `assignment_doc:` 行（PM 厳密運用がある場合）|
| A3 | `docs/design/<id>-delivery-io.md` | ファイル存在 |
| A4 | `skills/<id>/<pm-slug>/SKILL.md` | ファイル存在 |
| A5 | `workflows/agent-registry.yaml` | PM slug が `enabled: true` で登録 |
| B1 | `dispatch-request.v1.schema.json` | `department` enum に `<id>` |
| B2 | `dept-work-complete.v1.schema.json` | 同上 |
| B3 | `asana-buddy-handoff.v1.2.schema.json` | 同上 |
| C1 | `dept-work-io.md` | `<id>` 言及 |
| C2 | `handoff-v12-department.md` | `<id>` 言及 |
| C3 | `team-conventions.md` | `` `<id>` `` 言及 |
| C4 | `department-model.md` | `<id>` 言及 |
| C5 | `task-dispatcher/SKILL.md` | `<id>` 言及 |
| C7 | `issue-story-planner/SKILL.md` | `<id>` 言及 |
| C9 | `docs/inventory/skills-inventory.md` | PM slug 言及 |
| C11 | `README.md` | `<id>` または PM slug 言及 |
| C12 | `dispatch-prompt-ssot.md` | `## <id>` 節が存在 |
| D1 | `docs/design/<id>-pm-assignment.md` | ファイル存在（PM 厳密運用 department のみ） |
| E1 | `skills/planning/issue-story-planner/examples/handoff*.json` | いずれかが `"department": "<id>"` を含む |

### 実行モード

| モード | 振る舞い |
|--------|----------|
| `--department <id>` | 上記項目を `<id>` で実行。未該当を列挙 → exit 1 |
| `--all` | enabled 全 department を順次実行 |
| `--include-optional` | C7 など任意項目も含める |

## 完了条件

- A2: `validate_org_registry.py` exit 0、新規 5 項目が **enabled department 漏れ**を検知できる
- B: `check_new_department.py --department audit` exit 0、`--department planning` exit 0
- 既存の `new-department-checklist.md` を更新し、「機械チェック」セクションに `check_new_department.py` を案内

## やらないこと（中期施策）

- `organizations.yaml` → schema enum **自動生成**（A） — 別エピック
- `team-conventions.md` 比較表の自動生成（D） — 別エピック
- SSOT 階層化 / ディレクトリ分割（C） — 別エピック

## 参照

- 分析根拠: 直近の整合性ぬけ原因（5 連続 SSOT 修正コミット · 8 箇所重複 · 12〜15 箇所更新）
- `docs/design/new-department-checklist.md`
- `tools/validate_org_registry.py`
