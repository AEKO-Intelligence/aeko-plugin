---
name: generate-faq
description: >
  Deprecated. FAQ content + FAQPage JSON-LD are now produced inline by
  /aeko-run-action when the Plan.md's sections_required includes `faq`.
  This wrapper exists for one release cycle.
argument-hint: "(deprecated)"
allowed-tools: []
---

# generate-faq — Deprecated

Retired in the 2026-04 MCP consolidation. FAQ generation is no longer a standalone skill — it runs as part of `aeko-run-action` whenever the Plan.md's `frontmatter.sections_required` includes `faq` AND `pdp_responsive_contract.faq_jsonld_required == true`.

The new flow:
- Derives FAQ questions from `frontmatter.prompts_to_rank_on` when the Sonnet prose doesn't surface FAQ content. This guarantees the FAQ matches the exact AI-engine queries the plan is trying to rank for.
- Emits both visible HTML and `FAQPage` JSON-LD, kept in sync (same questions, equivalent answers).
- Applies contract §3.4 citability rules (80-150 word answers, explicit subject naming, direct 1-2 sentence lede).

## What to do instead

1. `/aeko-action-center <domain_id>` — pick a pending Action-tab item (PDP or own-content).
2. `/aeko-run-action <item_id>` — the FAQ block is generated automatically.

If you need FAQ content outside an Action item (rare), describe what you want in plain language — I'll draft it without running a retired skill.
