# org-os カーネル化 — development delivery

| 項目 | 内容 |
|------|------|
| エピック | `1215127084158665` |
| Phase 1 子 | `1215127324141338` |
| Phase 2 子 | `1215127381970812` |
| Phase 3+4 子 | `1215127412041925` |
| 日付 | 2026-05-26 |

## 概要

Asana CF を SSOT とする org-os カーネル（syscall + queue）を実装。OS Suspend Reason は Asana enum 表示名（`Approval` / `Human Review` / `External Block`）を使用。

## 変更点

| ファイル | 内容 |
|---------|------|
| `products/org-os/src/org_os/syscall.py` | start / suspend / resume / complete / init_epic |
| `products/org-os/src/org_os/queue.py` | ready_queue / wait_list (FIFO) |
| `products/org-os/src/org_os/constants.py` | Asana 表示名定数 |
| `products/org-os/src/org_os/cli.py` | queue · syscall サブコマンド |
| `tools/sync_org_os_cf_env.py` | OS Suspend Reason CF 同期 |
| `tools/approval_helper.py` | syscall.resume |
| `tools/wakuoke_resume_scan.py` | queue.ready_queue |
| `skills/.../create_approval_subtask.py` | syscall.suspend(Approval) + @mention |
| `skills/.../asana_program_common.py` | init_epic → syscall.init_epic |

## 検証

| コマンド | 結果 |
|---------|------|
| `org-os queue ready/wait --json` | ✅ project 1214771428861230 |
| `org-os watch --once` | ✅ |
| `org-os syscall start/suspend --dry-run` | ✅ Approval enum |
| `wakuoke_resume_scan --dry-run` | ✅ |
| `validate_ssot_contract.py` | ✅ |

## 関連

- SSOT v2.0: [`docs/design/org-os-product-io.md`](../design/org-os-product-io.md)
- Handoff: `output/planning/handoff/handoff.os-kernelize.json`
