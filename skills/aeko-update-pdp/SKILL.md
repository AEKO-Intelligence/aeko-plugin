---
name: aeko-update-pdp
description: >
  Deprecated. PDP update now runs through /aeko-run-action against a
  backend-authored Plan.md. This wrapper exists for one release cycle.
argument-hint: "(deprecated)"
allowed-tools: []
---

# aeko-update-pdp — Deprecated

Retired in the 2026-04 MCP consolidation. PDP updates are now driven by backend-authored Plan.md documents consumed by `aeko-run-action`.

## What to do instead

1. `/aeko-action-center <domain_id>` — see pending Action-tab items.
2. Pick the PDP item and copy its `item_id`.
3. `/aeko-run-action <item_id>`.

The new flow replaces v2-suggestion briefs (which this skill relied on) with the dual-format Plan.md contract. Required JSON-LD types, must-include items, FAQ coverage, sections_required, and responsive HTML rules all live in the Plan's frontmatter. See `docs/contracts/action-item-contract.md` §3.

Do NOT execute update logic from this skill — the v2 brief tools it called have been superseded.
