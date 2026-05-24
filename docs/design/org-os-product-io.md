# org-ops ↔ org-os プロダクト I/O 契約

| 項目 | 内容 |
|------|------|
| 版 | 1.0 |
| エピック | `1215088809649925` |
| governance 子 | `1215089088552096` |
| 参照 Handoff | `output/planning/handoff/handoff.org-os-triage.json` v3 |

## 1. 目的

**和久桶 L1（triage 拡張）** と **org-os 外部プロダクト** の責務境界を SSOT 化する。org-ops は org-meta / workflow / bootstrap を担い、epic 状態機械本体は org-os パッケージに集約する。

## 2. コンポーネント境界

```
┌─────────────────────────────────────────────────────────────┐
│ org-operations-agents (org-ops)                              │
│  L1: intake → triage → bootstrap → dispatch                 │
│  asana-buddy: handoff_to_asana · init_epic_os_state          │
│  tools: intake_triage · auto_intake_runner · sync_org_os_cf  │
│  tools/org_os.py  ──────────CLI ラッパー──────────────────┐ │
└─────────────────────────────────────────────────────────────│─┘
                                                              │
┌─────────────────────────────────────────────────────────────▼─┐
│ products/org-os/ (外部プロダクト)                              │
│  org-os status · dispatch · watch                             │
│  state_machine · asana_client (CF read/write)                 │
└───────────────────────────────────────────────────────────────┘
```

| 側 | 担う | 担わない |
|----|------|----------|
| **org-ops** | triage · bootstrap · planning dispatch · `.env` GID sync · 新 epic の OS State 初期化 | 状態機械本体 · Running/Waiting 遷移の常時監視 |
| **org-os** | epic CF read/write · Ready→Running dispatch · watch | intake · Handoff · CF フィールド作成 |

## 3. L1 workflow（default v4）

SSOT: [`workflows/default.yaml`](../../workflows/default.yaml)

| step | agent | 出力 |
|------|-------|------|
| intake | workflow-orchestrator | snapshot |
| triage | workflow-orchestrator | `output/platform/triage/<gid>-epic-input.json` |
| bootstrap | asana-buddy | Asana 親 + 企画子 |
| dispatch | task-dispatcher | planning-pm |

**禁止:** triage 専用の parallel epic-generator。epic 作成は **bootstrap / handoff_to_asana** のみ。

epic_input schema: [`schemas/platform/epic-input.v1.schema.json`](../../schemas/platform/epic-input.v1.schema.json)

## 4. Asana カスタムフィールド

### 4.1 フィールド（依頼者が Asana プロジェクトに追加）

| フィールド | enum | 用途 |
|-----------|------|------|
| **OS State** | Ready / Running / Waiting / Done | epic 状態機械 |
| **Approval Required** | Yes / No | 人間承認要否（【承認】サブと整合） |

**開発スコープ外:** CF 作成。依頼者追加後に GID を sync する。

### 4.2 env キー命名（`.env`）

sync CLI: [`tools/sync_org_os_cf_env.py`](../../tools/sync_org_os_cf_env.py)

| env キー | 内容 |
|---------|------|
| `ASANA_OS_STATE_FIELD_GID` | OS State フィールド GID |
| `ASANA_OS_STATE_READY_GID` | Ready enum GID |
| `ASANA_OS_STATE_RUNNING_GID` | Running enum GID |
| `ASANA_OS_STATE_WAITING_GID` | Waiting enum GID |
| `ASANA_OS_STATE_DONE_GID` | Done enum GID |
| `ASANA_APPROVAL_REQUIRED_FIELD_GID` | Approval Required フィールド GID |
| `ASANA_APPROVAL_REQUIRED_YES_GID` | Yes enum GID |
| `ASANA_APPROVAL_REQUIRED_NO_GID` | No enum GID |

テンプレート: [`skills/platform/asana-buddy/optional/.env.example`](../../skills/platform/asana-buddy/optional/.env.example)

### 4.3 bootstrap 時初期化

`handoff_to_asana.py` create モード成功後:

- OS State = **Ready**
- Approval Required = **No**

実装: `asana_program_common.init_epic_os_state`

## 5. org-os CLI 契約

パッケージ: [`products/org-os/`](../../products/org-os/) · wrapper: [`tools/org_os.py`](../../tools/org_os.py)

| コマンド | 説明 | 前提 |
|---------|------|------|
| `org-os status --epic <GID>` | 現在 OS State を JSON 出力 | env GID 設定済み |
| `org-os dispatch --epic <GID>` | Ready → Running | os_state=Ready |
| `org-os watch --project <GID> [--once]` | Ready/Waiting epic を列挙 | env GID 設定済み |

### 状態遷移（プロダクト内）

```
Ready --(dispatch)--> Running
Running --(need_approval)--> Waiting
Waiting --(approval_done)--> Ready
Running --(complete)--> Done
```

`need_approval` / `approval_done` / `complete` は state_machine API に存在。CLI 公開は将来拡張可。

## 6. asana-driven-ops 役割分担

| Phase | org-ops | org-os |
|-------|---------|--------|
| Phase 4 auto-intake | `auto_intake_runner`（triage 統合）· poller `--auto-bootstrap` | 未使用（bootstrap 後に任意） |
| planning gate | `--record-wait` · RESUME | — |
| execution dispatch | task-dispatcher → 各 PM | epic Ready 時 `dispatch` フック（将来） |
| epic 完了 | comment_epic_summary · complete | `Done` 遷移（将来連携） |

参照: [`asana-driven-ops.md`](asana-driven-ops.md) Phase 4 · [`workflow-io-contract.md`](workflow-io-contract.md)

## 7. 開発 / governance / audit 配賦

| 子 | department | 成果物 |
|----|------------|--------|
| 【2/5】triage | development | workflow · triage CLI · sync CLI |
| 【3/5】org-os | development | `products/org-os/` |
| 【4/5】境界 SSOT | governance | **本ファイル** |
| 【5/5】監査 | audit | ConsistencyAuditReport · AuditReviewResult |

## 8. 検証

```powershell
python tools/sync_org_os_cf_env.py --project <PROJECT_GID> --dry-run
python tools/org_os.py status --epic <PARENT_GID>
python tools/validate_ssot_contract.py
```

## 9. 関連

- triage dryrun: [`../verification/org-os-triage-workflow-dryrun.md`](../verification/org-os-triage-workflow-dryrun.md)
- org-os dryrun: [`../verification/org-os-product-dryrun.md`](../verification/org-os-product-dryrun.md)
- dev delivery retro: [`../verification/org-os-dev-delivery-retro.md`](../verification/org-os-dev-delivery-retro.md)
