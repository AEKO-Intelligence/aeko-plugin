---
name: aeo-optimize
description: >
  Deprecated. Use /aeko-action-center to pick a pending PDP item,
  then /aeko-run-action to execute it. This wrapper exists for one
  release cycle so historical references still route users correctly.
argument-hint: "(deprecated)"
allowed-tools: []
---

# aeo-optimize — Deprecated

This skill has been retired as part of the 2026-04 MCP consolidation. The full-PDP-optimization flow (description + Product JSON-LD + FAQPage JSON-LD + Review JSON-LD + citability-tuned prose) now lives in `aeko-run-action`, driven by a backend-authored Plan.md.

## What to do instead

1. Run `/aeko-action-center <domain_id>` to see pending Action-tab items for the domain.
2. Pick the PDP item you want to optimize. Copy its `item_id`.
3. Run `/aeko-run-action <item_id>`.

The new flow produces the same artifacts (optimized description, Product JSON-LD, FAQPage JSON-LD, optional Review JSON-LD) plus a few things the old skill didn't:
- Backend-generated plan with the full prompt / brand-kit / OCR context pre-loaded
- Shadow-product write-back (non-selling draft) by default — safer than manual copy-paste
- Strategy prompt: keep current images, rebuild from existing images, or rebuild with local files
- `[VERIFY: ...]` markers for missing data instead of fabricated values

Tell the user this upfront and route them. Do NOT execute any optimization logic from this skill — the tools it used (`aeko_get_suggestions`, `aeko_get_page_analysis`, `aeko_preview_optimized_page`) are retired and will error.
