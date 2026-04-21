---
name: aeko-optimize-pdp
description: >
  Deprecated. PDP optimization now runs through /aeko-run-action.
  This wrapper exists for one release cycle.
argument-hint: "(deprecated)"
allowed-tools: []
---

# aeko-optimize-pdp — Deprecated

Retired in the 2026-04 MCP consolidation. The merchant-first PDP optimization flow (rewrite strategy prompts, research depth, Cafe24/Shopify write-back) is now consolidated into `aeko-run-action`, driven by a backend-authored Plan.md.

## What to do instead

1. `/aeko-action-center <domain_id>` — see pending Action-tab items for the domain.
2. Pick the PDP item and copy its `item_id`.
3. `/aeko-run-action <item_id>`.

The new flow still asks the user to pick an image strategy (keep current images / rebuild from existing / rebuild with local files), still supports Cafe24/Shopify write-back, and adds shadow-product-by-default so the live listing is never touched without explicit intent.

Do NOT execute optimization logic from this skill — the tool `aeko_deploy_pdp_html` is retired. `aeko_create_shadow_product` + `aeko_update_product_description` are the supported write surfaces in the new flow.
