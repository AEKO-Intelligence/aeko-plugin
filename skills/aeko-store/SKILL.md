---
name: aeko-store
description: >
  Sets up an AEKO domain and store or injects real customer reviews into the
  credential-less manual review source. Use mode=setup for domain, products,
  markets, quota, and starter prompts; use mode=reviews for merchant-provided
  or public-source review intake. Never fabricates products or reviews.
argument-hint: "[mode=setup|reviews] [domain-id-or-url]"
allowed-tools: aeko_list_domains, aeko_add_domain, aeko_get_domain_info, aeko_list_store_integrations, aeko_connect_store, aeko_sync_store, aeko_inject_products, aeko_list_store_products, aeko_update_markets, aeko_get_quota, aeko_generate_starter_prompts, aeko_accept_starter_prompts, aeko_inject_reviews, WebSearch, WebFetch, Read
---

# AEKO Store

Own two related workflows without blurring their safety rules: initial domain/store setup and real-review
intake. Mirror the user's chat language for questions, confirmations, errors, and summaries. Keep IDs,
country codes, platform values, product keys, JSON fields, paths, slash commands, and tool names in
English/ASCII. The brand mark is always `AEKO`.

## Select one mode

- `mode=setup` — add/select a domain, connect/sync Cafe24 or Shopify or inject manual products, verify
  products, set markets, inspect quota, and generate/accept starter prompts. Read
  `references/setup-mode.md` completely.
- `mode=reviews` — collect only genuine merchant-provided or public-source reviews, normalize and preview
  them, then inject into the manual review source. Read `references/review-intake-mode.md` completely.

Infer reviews mode from an explicit request to import/inject reviews; otherwise default to setup. Never run
both write flows behind one confirmation.

## Review intake boundary

`aeko_inject_reviews` is the **only review intake available to an agent**. AEKO deliberately does not expose
cre.ma, Judge.me, Cafe24, or any other review-platform credential connection/sync flow through MCP. Do not
imply those services can be connected here: direct the user to the AEKO dashboard for credentialed review
integrations, or use `mode=reviews` for the credential-less manual source.

