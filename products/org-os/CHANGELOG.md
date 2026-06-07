# Changelog

All notable changes to **org-os** follow [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-06-07

### Added

- `doctor` / `doctor --online` CLI for first-setup validation (A1)
- `backfill` helpers for legacy epic OS State (A2)
- Injectable HTTP boundary on `asana_client` (`set_http_handlers` / `reset_http_handlers`)
- Unit tests: syscall transitions, queue filters, `require_agent_id`, fake HTTP client
- Semver / syscall stability policy in `docs/design/org-os-product-io.md` §10

### Changed

- **Version** `0.1.0` → `1.0.0` — public syscall / queue API frozen for external consumers
- OS Suspend Reason uses **Asana enum display names** (`Approval`, `Human Review`, `External Block`) — not snake_case (contract v2.0)

### Notes

- org-ops repo consumers should pin `org-os==1.0.0` or use the monorepo `pip install -e products/org-os`
- Breaking changes after 1.0.0 require MAJOR bump per §10 syscall policy

## [0.1.0] - 2026-05 (pre-release)

- Initial extracted kernel: `syscall`, `queue`, `asana_client`, CLI wrapper via `tools/org_os.py`
